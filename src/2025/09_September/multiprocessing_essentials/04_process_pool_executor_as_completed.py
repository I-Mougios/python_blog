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
        secs = [5, 4, 3, 2, 1]
        idx = list(range(1, 6))
        results = [executor.submit(task, sec, idx) for sec, idx in zip(secs, idx)]

        # It will print the results in the order of completion time.
        # Notice results are not returned in the order they have started.

        # Is it possible to get the results in the order the processes were started
        # without breaking the concurrency ?
        for res in concurrent.futures.as_completed(results):
            print(f"{res.result()}")

    end = time.time()

    print("Main application running ...")
    print(f"Elapsed time: {end - start:.2f} seconds")
