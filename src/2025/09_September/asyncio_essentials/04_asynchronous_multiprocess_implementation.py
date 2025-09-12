"""
This module provides functionality to download a list of images concurrently from the web
and then process them (edge detection) using parallel CPU-bound tasks. It is designed
to maximize performance by combining asynchronous I/O with process-based parallelism.

Key Features:
-------------
1. **Concurrent Downloads (Network I/O bound)**
   - Uses `httpx.AsyncClient` for non-blocking HTTP requests.
   - Downloads are limited using an `asyncio.Semaphore` to control the maximum
     number of concurrent requests (`DOWNLOAD_LIMIT`).
   - Images are written to disk asynchronously using `aiofiles`, allowing the
     event loop to continue scheduling other tasks during file I/O.

2. **Concurrent Image Processing (CPU-bound)**
   - Edge detection is applied to each image using PIL (`Image` module).
   - Processing is performed in parallel using a `ProcessPoolExecutor` to
     leverage multiple CPU cores (`NUM_WORKERS`).
   - `asyncio.get_event_loop().run_in_executor()` allows CPU-bound tasks
     to run without blocking the event loop.

3. **Timing and Performance Measurement**
   - A flexible `timer` decorator is used to measure execution time for both
     asynchronous and synchronous functions.
   - All timings are stored in a shared dictionary `timings`.

Implementation Details / Key Differences
----------------------------------------
- Concurrent downloads are limited to `DOWNLOAD_LIMIT` using an `asyncio.Semaphore`.
- CPU-bound image processing is parallelized across multiple processes to utilize
  multiple CPU cores effectively.
"""

import asyncio
import inspect
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Callable, Iterable, Optional

import aiofiles
import httpx
import wrapt
from PIL import Image

IMAGE_URLS = [
    "https://images.unsplash.com/photo-1516117172878-fd2c41f4a759?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1532009324734-20a7a5813719?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1524429656589-6633a470097c?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1530224264768-7ff8c1789d79?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1564135624576-c5c88640f235?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1541698444083-023c97d3f4b6?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1522364723953-452d3431c267?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1516972810927-80185027ca84?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1550439062-609e1531270e?w=1920&h=1080&fit=crop",
    "https://images.unsplash.com/photo-1549692520-acc6669e2f0c?w=1920&h=1080&fit=crop",
]
NUM_WORKERS = os.cpu_count()
DOWNLOAD_LIMIT = 4

base_dir = Path(__file__).resolve().parent
raw_images_dir = base_dir / "raw_images"
processed_images_dir = base_dir / "processed_images"
timings = {}


def timer(func: Optional[Callable] = None, *, timings_dict: dict | None = None) -> Callable:

    if timings_dict is None:
        timings_dict = {}

    @wrapt.decorator
    async def async_wrapper(wrapped, instance, args, kwargs):
        start = time.time()
        result = await wrapped(*args, **kwargs)
        end = time.time()
        timings_dict[wrapped.__name__] = round((end - start), ndigits=4)
        return result

    @wrapt.decorator
    def sync_wrapper(wrapped, instance, args, kwargs):
        start = time.time()
        result = wrapped(*args, **kwargs)
        end = time.time()
        timings_dict[wrapped.__name__] = round((end - start), ndigits=4)
        return result

    def choose_wrapper(fn):
        if inspect.iscoroutinefunction(fn):
            return async_wrapper(fn)
        else:
            return sync_wrapper(fn)

    return choose_wrapper(func) if callable(func) else choose_wrapper


async def download_single_image(client: httpx.AsyncClient, url: str, idx: int, semaphore: asyncio.Semaphore) -> Path:
    async with semaphore:
        print(f"Downloading image {idx} from {url}")
        ts = int(time.time())
        url = f"{url}?{ts=}"
        response = await client.get(url, follow_redirects=True, timeout=5)
        response.raise_for_status()

        download_path = raw_images_dir / f"image_{idx}.png"

        # print(f"Start writing to {download_path}")
        async with aiofiles.open(download_path, "wb") as f:
            async for chunk in response.aiter_bytes(chunk_size=8192):
                await f.write(chunk)
        # print(f"Complete writing to {download_path}")

        print(f"Image {idx} saved to {download_path}")
        return download_path


@timer(timings_dict=timings)
async def download_images(urls: Iterable[Path | str]) -> Iterable[Path]:
    semaphore = asyncio.Semaphore(DOWNLOAD_LIMIT)
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(download_single_image(client, url, idx, semaphore)) for idx, url in enumerate(urls)]
            # async.TaskGroup context manager executes the tasks on exiting

    downloaded_images = [task.result() for task in tasks]
    print(f"Downloaded {len(downloaded_images)} images")
    return downloaded_images


def process_single_image(orig_path: Path) -> Path:
    save_path = processed_images_dir / orig_path.name

    with Image.open(orig_path) as img:
        data = list(img.getdata())
        width, height = img.size
        new_data = []

        for i in range(len(data)):
            current_r, current_g, current_b = data[i]

            total_diff = 0
            neighbor_count = 0

            for dx, dy in [(1, 0), (0, 1)]:
                x = (i % width) + dx
                y = (i // width) + dy

                if 0 <= x < width and 0 <= y < height:
                    neighbor_r, neighbor_g, neighbor_b = data[y * width + x]
                    diff = abs(current_r - neighbor_r) + abs(current_g - neighbor_g) + abs(current_b - neighbor_b)
                    total_diff += diff
                    neighbor_count += 1

            if neighbor_count > 0:
                edge_strength = total_diff // neighbor_count
                if edge_strength > 30:
                    new_data.append((255, 255, 255))
                else:
                    new_data.append((0, 0, 0))
            else:
                new_data.append((0, 0, 0))

        edge_img = Image.new("RGB", (width, height))
        edge_img.putdata(new_data)
        edge_img.save(save_path)

    print(f"Processed {orig_path} and saved to {save_path}")
    return save_path


@timer(timings_dict=timings)
async def process_images(orig_paths: Iterable[Path]) -> Iterable[Path]:
    loop = asyncio.get_event_loop()

    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        tasks = [loop.run_in_executor(executor, process_single_image, image_path) for image_path in orig_paths]

        processed_images = await asyncio.gather(*tasks)
    print(f"Processed {len(processed_images)} images")
    return processed_images


if __name__ == "__main__":
    if not raw_images_dir.exists():
        raw_images_dir.mkdir(parents=True, exist_ok=True)
    if not processed_images_dir.exists():
        processed_images_dir.mkdir(parents=True, exist_ok=True)

    downloaded_images_paths: Iterable[Path] = asyncio.run(download_images(IMAGE_URLS))
    processed_images_path: Iterable[Path] = asyncio.run(process_images(downloaded_images_paths))

    for key, value in timings.items():
        print(f"Function {key} took {value} seconds")
