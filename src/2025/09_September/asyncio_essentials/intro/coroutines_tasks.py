import asyncio


async def boil_water() -> None:
    print("Boiling water started")
    await asyncio.sleep(2)
    print("Boiling water finished")


async def brew_tea() -> None:
    print("Brewing tea started")
    await asyncio.sleep(1)
    print("Brewing tea finished")


async def serve_tea() -> None:
    print("Serving tea started")
    await asyncio.sleep(0.5)
    print("Tea is served!")


async def sequential_execution() -> None:
    print("Sequential execution started")
    # await statement does two things:
    #  1. add the coroutines to event loop
    #  2. execute them
    # what we wanted is to add both three routines to the event loop and then execute them concurrently
    await boil_water()
    await brew_tea()
    await serve_tea()


async def concurrent_execution() -> None:
    print("Concurrent execution started")
    # Boil water and brew tea added to the event loop and then executed concurrently
    tasks = asyncio.gather(boil_water(), brew_tea())
    await tasks
    # Serve tea only after both are done
    await serve_tea()


async def concurrent_using_tasks() -> None:
    print("Concurrent using tasks started")
    boil_water_task = asyncio.create_task(boil_water())
    brew_tea_task = asyncio.create_task(brew_tea())
    serve_tea_task = asyncio.create_task(serve_tea())
    await boil_water_task
    await brew_tea_task
    await serve_tea_task


if __name__ == "__main__":
    asyncio.run(sequential_execution())
    print("---" * 20)
    asyncio.run(concurrent_execution())
    print("---" * 20)
    asyncio.run(concurrent_using_tasks())
