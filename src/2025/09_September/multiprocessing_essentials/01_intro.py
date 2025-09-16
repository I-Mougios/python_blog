"""
Each process has its own memory space and its own Python interpreter (so its own GIL).
The start() method spawns a new process for each task and begins its execution,
but it does not block the main program from continuing to run.

"""

import multiprocessing
import time


def task(i):
    print(f"Task {i} started ...")
    time.sleep(1)
    print(f"Task {i} finished ...")


if __name__ == "__main__":
    tasks = [multiprocessing.Process(target=task, args=(i,)) for i in range(3)]

    start = time.time()

    # Start all tasks
    for t in tasks:
        t.start()

    end = time.time()

    print("Main application running ...")
    print(f"Elapsed time: {end - start:.2f} seconds")
