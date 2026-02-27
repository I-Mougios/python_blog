# src/2025/09_September/asyncio_essentials/08_async_batch_db_transactions.py

import asyncio
import io
import random
from csv import DictReader
from itertools import batched

import sqlalchemy as sa
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# DB Section
DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared"
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"uri": True},
)
async_session = async_sessionmaker(engine, expire_on_commit=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Persons(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String())
    age: Mapped[int] = mapped_column(Integer())
    gender: Mapped[str] = mapped_column(String(1))


async def check_connection():
    try:
        async with engine.begin() as connection:
            await connection.execute(sa.text("SELECT 1"))
    except Exception:
        print("Database connection failed")
    finally:
        await engine.dispose()


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all, checkfirst=True)

    await engine.dispose()


# File section
def in_memory_file(nrows=10):
    file = io.StringIO()
    file.write("name,age,gender\n")
    names = ["Jonny", "Janes", "Mary", "Larry"]
    ages = [18, 19, 20, 20, 30, 50, 40]
    genders = ["M", "F"]
    for _ in range(nrows):
        file.write(f"{random.choice(names)},{random.choice(ages)},{random.choice(genders)}\n")
    file.seek(0)
    return file


async def insert_csv():
    # SETUP
    await create_tables()
    csv_file = in_memory_file(nrows=10)
    headers = next(csv_file).rstrip("\n").split(",")
    batches = batched(csv_file, n=2, strict=False)
    # Start DB Calls
    try:
        async with async_session() as session:
            async with session.begin():
                for batch in batches:
                    rows = list(DictReader(batch, fieldnames=headers))
                    async with session.begin_nested():
                        await session.execute(sa.insert(Persons.__table__).values(rows))
                        await asyncio.sleep(random.random())
    finally:
        await engine.dispose()


# Requests
async def handle_request(id_):
    print(f"handling request: {id_}")
    await asyncio.sleep(random.random())
    print(f"done: {id_}")


async def main():
    requests = [asyncio.create_task(handle_request(_)) for _ in range(10)]
    insert_csv_task = asyncio.create_task(insert_csv())
    tasks = requests + [insert_csv_task]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
