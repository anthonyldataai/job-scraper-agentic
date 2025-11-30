import asyncio
from job_scraper import scrape_all_jobs

if __name__ == "__main__":
    asyncio.run(scrape_all_jobs(test_mode=True))
