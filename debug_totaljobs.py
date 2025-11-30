import asyncio
from playwright.async_api import async_playwright
import urllib.parse

KEYWORDS = "Technical Project Manager"
INDUSTRIES = [
    "Fintech",
    "Security Brokers",
    "Capital Market",
    "Asset Management",
    "Fund House"
]
OR_GROUP = " OR ".join([f'"{ind}"' for ind in INDUSTRIES])
SEARCH_QUERY = f'"{KEYWORDS}" AND ({OR_GROUP})'

async def debug_totaljobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        encoded_query = urllib.parse.quote(SEARCH_QUERY)
        url = f"https://www.totaljobs.com/jobs/{encoded_query}"
        print(f"Navigating to: {url}")
        
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(5000) # Wait a bit for things to settle
            
            # await page.screenshot(path="totaljobs_debug.png")
            # print("Screenshot saved to totaljobs_debug.png")
            
            # content = await page.content()
            # with open("totaljobs_debug.html", "w", encoding="utf-8") as f:
            #     f.write(content)
            # print("HTML saved to totaljobs_debug.html")

            links = await page.query_selector_all("a")
            print(f"Found {len(links)} links.")
            for i, link in enumerate(links[:50]): # Print first 50
                href = await link.get_attribute("href")
                text = await link.inner_text()
                print(f"{i}: {text.strip()} -> {href}")

            
        except Exception as e:
            print(f"Error: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_totaljobs())
