import concurrent.futures
import time


def task(secs, idx):
    print(f"Task {idx} started ...")
    time.sleep(secs)
    print(f"Task {idx} finished ...")
    return f"Done task {idx}"


if __name__ == "__main__":

    start = time.time()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # When calling to get the result of a future, it waits until the process is completed.
        f1 = executor.submit(task, 2, 1)  # return a future object
        print(f1.result())
        f2 = executor.submit(task, 1, 2)
        print(f2.result())

    end = time.time()

    print("Main application running ...")
    print(f"Elapsed time: {end - start:.2f} seconds")
