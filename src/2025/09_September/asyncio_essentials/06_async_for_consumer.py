import asyncio
import sys


async def simple_task(sleep_time, identifier):
    print(f"--> Starting task {identifier}")  # noqa: T201
    await asyncio.sleep(sleep_time)
    print(f"--> Task {identifier} finished")  # noqa: T201


async def main():
    print("Event loop started ...")  # noqa: T201
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    print("System Ready. Enter: <seconds> <name> (e.g., '3 MyTask')")  # noqa: T201
    async for line in reader:
        # Move the try/except INSIDE the loop
        try:
            data = line.decode().strip()
            if not data:
                continue

            parts = data.split(maxsplit=1)
            if len(parts) < 2:
                print("Error: Use format '<seconds> <name>'")  # noqa: T201
                continue

            sleep_time, identifier = parts
            # This is the line that caused the 'Listener error'
            asyncio.create_task(simple_task(int(sleep_time), identifier))

        except ValueError:
            print("Invalid input")  # noqa: T201
        except Exception as e:
            print(f"Unexpected error: {e}")  # noqa: T201

    print("[Ctrl + D] Cleaning up ...")  # noqa: T201
    running_tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    if running_tasks:
        print(f"Running tasks: {running_tasks!r}")  # noqa: T201
        await asyncio.wait(running_tasks, timeout=10)


if __name__ == "__main__":
    asyncio.run(main())
