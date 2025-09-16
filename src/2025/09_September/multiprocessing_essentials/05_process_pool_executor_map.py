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
        idxs = list(range(1, 6))
        results = executor.map(task, secs, idxs)

        # Notice that we achieved concurrency in our code
        # Each process completed based on their own workload
        # The results are returned in the order that they were started
        for res in results:
            print(f"{res=}")

    end = time.time()

    print("Main application running ...")
    print(f"Elapsed time: {end - start:.2f} seconds")
