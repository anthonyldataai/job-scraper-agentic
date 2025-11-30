import asyncio
from playwright.async_api import async_playwright
from job_scraper import scrape_linkedin, parse_relative_date
from utils.persistence import log_agent_action
import json

async def test_linkedin_only():
    """Test LinkedIn scraper with 10 jobs limit"""
    log_agent_action("Test", "Starting LinkedIn-only test (10 jobs)", status="INFO")
    
    all_jobs = []
    limit = 10
    keyword = "Technical Project Manager"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        log_agent_action("Test", f"Scraping LinkedIn for: {keyword} (limit={limit})", status="INFO")
        linkedin_jobs = await scrape_linkedin(page, keyword, limit=limit)
        all_jobs.extend(linkedin_jobs)
        
        await browser.close()
    
    log_agent_action("Test", f"Test complete. Found {len(all_jobs)} jobs on LinkedIn", status="SUCCESS")
    print(f"\n=== Test Results ===")
    print(f"Total jobs found: {len(all_jobs)}")
    print(f"\nFirst 3 jobs:")
    for i, job in enumerate(all_jobs[:3], 1):
        print(f"\n{i}. {job['Title']}")
        print(f"   Company: {job['Company']}")
        print(f"   Location: {job['Location']}")
        print(f"   Link: {job['Link']}")
    
    return all_jobs

if __name__ == "__main__":
    asyncio.run(test_linkedin_only())
