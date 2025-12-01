import asyncio
from playwright.async_api import async_playwright

async def test_linkedin_connectivity():
    print("Testing connectivity to LinkedIn...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            response = await page.goto("https://www.linkedin.com", timeout=30000)
            if response:
                print(f"Success! Status code: {response.status}")
                print(f"Page title: {await page.title()}")
            else:
                print("Failed to get response (None)")
        except Exception as e:
            print(f"Error connecting to LinkedIn: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_linkedin_connectivity())
