import asyncio
from playwright.async_api import async_playwright
import urllib.parse

KEYWORDS = "Technical Project Manager"

async def debug_reed_card():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        encoded_keywords = urllib.parse.quote(KEYWORDS)
        url = f"https://www.reed.co.uk/jobs?keywords={encoded_keywords}&location=London&sortby=DisplayDate"
        
        print(f"Navigating to: {url}")
        await page.goto(url, timeout=60000)
        
        # Handle cookie consent
        await asyncio.sleep(2)
        try:
            reject_btn = await page.query_selector('button:has-text("Reject All")')
            if reject_btn:
                print("Clicking 'Reject All'...")
                await reject_btn.click()
                await asyncio.sleep(2)
        except:
            pass
        
        await asyncio.sleep(2)
        
        # Get first job card
        job_cards = await page.query_selector_all('article.job-result')
        if job_cards:
            print(f"\nFound {len(job_cards)} job cards")
            first_card = job_cards[0]
            
            # Get all text from the card
            card_text = await first_card.inner_text()
            print(f"\n=== FIRST JOB CARD TEXT ===")
            print(card_text)
            print("=" * 50)
            
            # Try to find all elements with date-like content
            print("\n=== SEARCHING FOR DATE ELEMENTS ===")
            all_elements = await first_card.query_selector_all('*')
            for el in all_elements[:20]:  # Check first 20 elements
                text = await el.inner_text()
                if text and len(text) < 50:  # Short text only
                    tag = await el.evaluate('el => el.tagName')
                    class_name = await el.get_attribute('class')
                    print(f"{tag}.{class_name}: {text}")
        
        print("\nBrowser will stay open for 30 seconds...")
        await asyncio.sleep(30)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_reed_card())
