"""
In contrast to module 01_intro, here we want the spawned processes to complete
before moving on to the rest of the program.

To achieve this, we use the join() method, which blocks the main program
until the corresponding process finishes execution.

join() method
    - Purpose: Waits for a thread or process to finish execution.
    - Behavior: Blocks the calling program until the target thread or process completes.
  Usage: Called after start()

Moreover, our main program need access to the output of each process so we need an IPC mechanism
(inter-process communication).
Notice that queue belongs to the global namespace
"""

import multiprocessing
import time


def task(i, queue):
    print(f"Task {i} started ...")
    time.sleep(1)
    result = i * 2
    print(f"Task {i} finished ...")
    queue.put(result)  # put the result in the queue


if __name__ == "__main__":
    q = multiprocessing.Queue()
    tasks = [multiprocessing.Process(target=task, args=(i, q)) for i in range(3)]

    start = time.time()

    # Start all tasks
    for t in tasks:
        t.start()

    # Wait for all tasks to finish
    for t in tasks:
        t.join()

    # Collect results from the queue
    results = [q.get() for _ in range(3)]

    end = time.time()

    print("Main application running ...")
    print(f"Results: {results}")
    print(f"Elapsed time: {end - start:.2f} seconds")
