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

async def debug_reed():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        encoded_full_query = urllib.parse.quote(SEARCH_QUERY)
        url = f"https://www.reed.co.uk/jobs?keywords={encoded_full_query}&location=London&sortby=DisplayDate"
        
        print(f"Navigating to: {url}")
        await page.goto(url, timeout=60000)
        
        # Wait for cookie dialog
        print("Waiting for page to load...")
        await asyncio.sleep(3)
        
        # Try to find and click cookie buttons
        print("Looking for cookie consent buttons...")
        try:
            # Try "Reject All" first
            reject_btn = await page.query_selector('button:has-text("Reject All")')
            if reject_btn:
                print("Found 'Reject All' button, clicking...")
                await reject_btn.click()
                await asyncio.sleep(2)
            else:
                print("No 'Reject All' button found, trying 'Accept All'...")
                accept_btn = await page.query_selector('button:has-text("Accept All")')
                if accept_btn:
                    print("Found 'Accept All' button, clicking...")
                    await accept_btn.click()
                    await asyncio.sleep(2)
                else:
                    print("No cookie buttons found")
        except Exception as e:
            print(f"Error handling cookies: {e}")
        
        # Check for job results
        print("Looking for job results...")
        try:
            await page.wait_for_selector('article.job-result', timeout=10000)
            job_cards = await page.query_selector_all('article.job-result')
            print(f"Found {len(job_cards)} job cards")
            
            if len(job_cards) > 0:
                # Print first job details
                first_card = job_cards[0]
                title_el = await first_card.query_selector('h3.title a')
                if title_el:
                    title = await title_el.get_attribute('title')
                    print(f"First job title: {title}")
        except Exception as e:
            print(f"Error finding jobs: {e}")
            # Take screenshot
            await page.screenshot(path="reed_debug.png")
            print("Screenshot saved to reed_debug.png")
        
        # Keep browser open for manual inspection
        print("Browser will stay open for 30 seconds for manual inspection...")
        await asyncio.sleep(30)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_reed())
