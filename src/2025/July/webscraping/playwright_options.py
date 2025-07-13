import asyncio
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        # 1. Launch headless browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # 2. Go to page (wait until network is idle)
        await page.goto("https://www.bankofamerica.com", wait_until="load")

        # Take a screenshot
        screenshot_path = Path("screenshots/step1_basic.png")
        screenshot_path.parent.mkdir(exist_ok=True)
        await page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved at {screenshot_path}")

        # Save full HTML
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        pretty_html = soup.prettify()

        html_path = screenshot_path.with_suffix(".html")
        html_path.write_text(pretty_html, encoding="utf-8")
        print(f"HTML saved at {html_path}")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
    import requests

    url = "https://www.bankofamerica.com"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)

    # Save raw HTML content
    with open("boa_static.html", "w", encoding="utf-8") as f:
        f.write(BeautifulSoup(response.text, features="html.parser").prettify())

    print("✅ HTML content saved to 'boa_static.html'")
