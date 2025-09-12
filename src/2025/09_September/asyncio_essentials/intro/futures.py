import asyncio

import aiofiles

lines = ["Hello, World!", "Practise Asyncio ..."]


async def async_write(path: str) -> str:
    async with aiofiles.open(
        path,
        "w",
    ) as f:
        await f.write("\n".join(lines))
        return path


async def main(path: str) -> str:

    loop = asyncio.get_event_loop()
    future = loop.create_future()  # A promise-like object that wait a result
    print(f"Empty future: {future}")

    future.set_result(f"Filepath: {await async_write(path)}")
    future_result = await future
    print(f"Result -> {future_result}")


if __name__ == "__main__":
    asyncio.run(main("test_async_write"))
