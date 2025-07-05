import argparse
import sys
import time
from pathlib import Path

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

AVAILABLE_OPTIONS = {
    "normal": {
        "--headless",
        "--start-maximized",
        "--incognito",
        "--disable-gpu",
        "--disable-extensions",
        "--window-size",
        "--user-agent",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--remote-debugging-port",
        "--disable-blink-features",
        "--disable-popup-blocking",
        "--ignore-certificate-errors",
        "--disable-infobars",
        "--disable-notifications",
        "--lang",  # e.g., --lang=en
    },
    "experimental": {
        "excludeSwitches",  # expects a list, e.g., ["enable-automation"]
        "useAutomationExtension",  # expects a boolean
        "prefs",  # expects a dict, e.g., {"profile.default_content_setting_values.images": 2}
        "mobileEmulation",  # e.g., {"deviceName": "Pixel 2"}
        "detach",  # whether to keep the browser open after script ends
    },
}


def _validate_and_classify_option(opt: str) -> tuple[bool, str | None]:
    """
    Returns (is_valid, category) where category is 'normal' or 'experimental' or None if invalid.
    """

    if "=" in opt:
        key = opt.split("=", 1)[0]
    else:
        key = opt

    if key in AVAILABLE_OPTIONS["normal"]:
        return True, "normal"
    elif key in AVAILABLE_OPTIONS["experimental"]:
        return True, "experimental"
    return False, None


def demo_chrome_options(  # noqa: C901
    url: str, options: str | list[str], wait_time: int = 5, screenshot_name: str = None
) -> None:

    if isinstance(options, str):
        options = [options]

    if screenshot_name is None:
        screenshot_name = "screenshot"

    screenshot_dir = Path().cwd() / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    # Required setup for the driver
    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    chrome_options = ChromeOptions()

    experimental_opts = {}
    for opt in options:
        if "" == opt.strip():
            continue

        valid, category = _validate_and_classify_option(opt)
        if not valid:
            print(f"⚠️ Skipping unknown option: {opt}")
            continue

        if "=" in opt:
            key, val = opt.split("=", 1)
            if val.lower() in {"true", "false"}:
                val = val.lower() == "true"
            elif val.isdigit():
                val = int(val)
        else:
            key, val = opt, True

        if category == "normal":
            chrome_options.add_argument(opt)
        elif category == "experimental":
            experimental_opts[key] = val

    for key, val in experimental_opts.items():
        chrome_options.add_experimental_option(key, val)

    # Get url with options and save a screenshot
    driver_with_options = Chrome(service=service, options=chrome_options)
    driver_with_options.get(url)
    time.sleep(wait_time)
    driver_with_options.save_screenshot(
        str(
            (
                screenshot_dir
                / f"{screenshot_name}_{'_'.join(opt.replace('--', '')
                                                                    for opt in options)}.png"  # noqa: E127git
            )
        )
    )
    driver_with_options.quit()

    # Without options
    driver_plain = Chrome(service=service)
    driver_plain.get(url)
    time.sleep(wait_time)
    driver_plain.save_screenshot((str(screenshot_dir / "screenshot_without_options.png")))
    driver_plain.quit()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("✅ Available options:")

        print("\nNormal options:")
        for opt in sorted(AVAILABLE_OPTIONS["normal"]):
            print(f"  {opt}")

        print("\nExperimental options:")
        for opt in sorted(AVAILABLE_OPTIONS["experimental"]):
            print(f"  {opt}")

        print("\n🧪 Example usage:")
        print('  python options.py -u https://www.imdb.com --options "--headless=new --start-maximized"')
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Test Chrome options on a given URL.")
    parser.add_argument("-u", "--url", type=str, required=True, help="URL to open (e.g., https://www.imdb.com)")

    parser.add_argument(
        "-o",
        "--options",
        required=True,
        type=str,
        help="Chrome options (e.g., --headless=new --start-maximized)",
    )

    parser.add_argument("-w", "--wait-time", type=int, default=5, help="Time to wait before quitting each browser")

    parser.add_argument(
        "-s",
        "--screenshot_name",
        default=None,
        type=str,
        help="Custom screenshot filename for the version with options",
    )

    try:
        opt_idx = sys.argv.index("-o")
    except ValueError:
        opt_idx = sys.argv.index("--options")

    opts_args = sys.argv[opt_idx + 1]

    opt_args = opts_args if " " not in opts_args else " " + opts_args

    args = parser.parse_args()
    demo_chrome_options(
        url=args.url, options=args.options.split(" "), wait_time=args.wait_time, screenshot_name=args.screenshot_name
    )
