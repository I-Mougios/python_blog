# src/2025/09_September/asyncio_essentials/07_async_coro_in_for_loop.py
import asyncio
import io
import random


async def handle_request(id_):
    print(f"handling request: {id_}")
    await asyncio.sleep(random.random())
    print(f"done: {id_}")


async def run_event_loop():
    await asyncio.sleep(0)


async def read_file(f):
    for line in f:
        print(line, end="")
        await asyncio.sleep(0.2)
        print("----------")


def in_memory_file(nrows=10):
    file = io.StringIO()
    file.write("Name,Age,Gender\n")
    names = ["Jonny", "Janes", "Mary", "Larry"]
    ages = [18, 19, 20, 20, 30, 50, 40]
    genders = ["M", "F"]
    for _ in range(nrows):
        file.write(f"{random.choice(names)},{random.choice(ages)},{random.choice(genders)}\n")
    file.seek(0)
    return file


async def main():
    file = in_memory_file()

    tasks = []
    tasks.append(asyncio.create_task(read_file(file)))

    for i in range(4):
        tasks.append(asyncio.create_task(handle_request(i)))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
