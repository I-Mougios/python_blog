import time
from pathlib import Path
from typing import Iterable

import requests
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

base_dir = Path(__file__).resolve().parent
raw_images_dir = base_dir / "raw_images"
processed_images_dir = base_dir / "processed_images"
timings = {}


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        timings[func.__name__] = round((end - start), ndigits=3)
        return result

    return wrapper


def download_single_image(url: str, idx: int) -> Path:
    print(f"Downloading image {idx} from {url}")
    ts = int(time.time())
    url = f"{url}?{ts=}"
    response = requests.get(url, allow_redirects=True, timeout=5)
    response.raise_for_status()

    download_path = raw_images_dir / f"image_{idx}.png"

    with download_path.open("wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Image {idx} saved to {download_path}")
    return download_path


@timer
def download_images(urls: Iterable[Path | str]) -> Iterable[Path]:
    downloaded_images = [download_single_image(url, idx) for idx, url in enumerate(urls)]
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


@timer
def process_images(orig_paths: Iterable[Path]) -> Iterable[Path]:
    processed_images = [process_single_image(image_path) for idx, image_path in enumerate(orig_paths)]
    print(f"Processed {len(processed_images)} images")
    return processed_images


if __name__ == "__main__":
    if not raw_images_dir.exists():
        raw_images_dir.mkdir(parents=True, exist_ok=True)
    if not processed_images_dir.exists():
        processed_images_dir.mkdir(parents=True, exist_ok=True)

    downloaded_images_paths: Iterable[Path] = download_images(IMAGE_URLS)
    processed_images_path: Iterable[Path] = process_images(downloaded_images_paths)

    for key, value in timings.items():
        print(f"Function {key} took {value} seconds")
