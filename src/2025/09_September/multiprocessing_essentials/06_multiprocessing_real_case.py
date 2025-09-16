import asyncio
import concurrent.futures
import os
import time
from pathlib import Path
from typing import Iterable

import aiofiles
import httpx
from PIL import Image, ImageFilter

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

DOWNLOAD_LIMIT = 4
MAX_WORKERS = os.cpu_count()


def counter():
    cnt = 0

    def inc():
        nonlocal cnt
        cnt += 1
        return cnt

    return inc


cnt = counter()


async def download_single_image(
    url: str, client: httpx.AsyncClient, semaphore: asyncio.Semaphore, download_path: str = None
) -> str:

    async with semaphore:
        if not download_path:
            download_dir = Path(__file__).resolve().parent / "raw_images"
            download_dir.mkdir(parents=True, exist_ok=True)
            download_path = download_dir / f"image_{cnt()}.png"
        else:
            download_path = Path(download_path)
            download_dir = download_path.parent
            download_dir.mkdir(parents=True, exist_ok=True)

        print(f"Downloading image {download_path.name}")
        response = await client.get(url, timeout=5, follow_redirects=True)
        response.raise_for_status()

        async with aiofiles.open(download_path, mode="wb") as file:
            async for chunk in response.aiter_bytes(chunk_size=2048):
                await file.write(chunk)

        print(f"Image saved to {download_path.name}")

        return download_path


async def download_images(urls: Iterable[Path | str]) -> Iterable[Path]:
    semaphore = asyncio.Semaphore(DOWNLOAD_LIMIT)
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            download_tasks = [tg.create_task(download_single_image(url, client, semaphore)) for url in urls]

        download_paths = [download_task.result() for download_task in download_tasks]

    return download_paths


def process_image(image_path: Path, save_path: str | None = None) -> Path:
    print(f"Processing image {image_path}")
    if not save_path:
        processed_dir = Path(__file__).resolve().parent / "processed_images"
        processed_dir.mkdir(exist_ok=True, parents=True)
        save_path = processed_dir / image_path.name
    else:
        save_path = Path(save_path)
        save_path.parent.mkdir(exist_ok=True, parents=True)

    img = Image.open(image_path)
    processed_img = img.filter(ImageFilter.GaussianBlur(20))
    processed_img.thumbnail((1200, 1200))
    processed_img.save(save_path)
    print(f"Processed image save to {save_path.name}")
    return save_path


def process_images_concurrently(paths: Iterable[Path]) -> Iterable[Path]:
    # It is possible to switch to ThreadPoolExecutor since there are many I/O ops
    # Basically it will run faster with ThreadPoolExecutor because there is not a lot cpu computation
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(process_image, paths)

    return list(results)


if __name__ == "__main__":
    download_start = time.time()
    image_paths = asyncio.run(download_images(IMAGE_URLS))
    download_end = time.time()
    print("Downloading images completed ... ", end="\n\n")
    print(f"Download time: {download_end - download_start}")
    process_images_start = time.time()
    processed_image_paths = process_images_concurrently(image_paths)
    process_images_end = time.time()
    print("Processing images completed ... ", end="\n\n")
    print(f"Processing time: {process_images_end - process_images_start}")
