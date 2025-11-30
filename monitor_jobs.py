import asyncio
import pandas as pd
import os
import glob
from datetime import datetime
from job_scraper import scrape_all_jobs, save_jobs_to_excel
from plyer import notification

def send_notification(title, message):
    """Send a Windows toast notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Job Scraper',
            timeout=10
        )
    except Exception as e:
        print(f"Notification error: {e}")

def get_seen_links(directory="."):
    """
    Builds a set of all job links seen in the latest main file and subsequent new_jobs files.
    """
    seen_links = set()
    
    # 1. Find the latest main file (jobs_v*.xlsx or jobs_master.xlsx)
    # We look for files starting with "jobs_" but NOT "new_jobs_"
    main_files = [f for f in glob.glob(os.path.join(directory, "jobs_*.xlsx")) 
                  if not os.path.basename(f).startswith("new_jobs_")]
    
    latest_main_file = None
    if main_files:
        latest_main_file = max(main_files, key=os.path.getmtime)
        print(f"Latest main file: {latest_main_file}")
        try:
            df = pd.read_excel(latest_main_file)
            if 'Link' in df.columns:
                seen_links.update(df['Link'].astype(str).tolist())
        except Exception as e:
            print(f"Error reading {latest_main_file}: {e}")
            
    # 2. Find all new_jobs_*.xlsx files created AFTER the main file
    new_files = glob.glob(os.path.join(directory, "new_jobs_*.xlsx"))
    
    for f in new_files:
        # If we have a main file, only check new_jobs files that are newer than it
        if latest_main_file and os.path.getmtime(f) <= os.path.getmtime(latest_main_file):
            continue
            
        try:
            df = pd.read_excel(f)
            if 'Link' in df.columns:
                seen_links.update(df['Link'].astype(str).tolist())
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    print(f"Total seen jobs loaded: {len(seen_links)}")
    return seen_links

def main():
    print("Starting monitoring job...")
    
    # 1. Scrape current jobs
    current_jobs = asyncio.run(scrape_all_jobs())
    if not current_jobs:
        print("No jobs found during this run.")
        return

    # 2. Get set of already seen links
    seen_links = get_seen_links()
    
    # 3. Identify new jobs
    new_jobs = [job for job in current_jobs if job['Link'] not in seen_links]
        
    if new_jobs:
        print(f"Found {len(new_jobs)} POTENTIAL new jobs (before filtering).")
        
        # 4. Save new jobs using the main scraper's save function
        # This handles filtering (last 7 days), sorting, and formatting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"new_jobs_{timestamp}.xlsx"
        
        # save_jobs_to_excel will filter out old jobs. 
        # We need to check if any remained after saving.
        save_jobs_to_excel(new_jobs, new_filename)
        
        # Check if file was created and has rows
        if os.path.exists(new_filename):
            try:
                df = pd.read_excel(new_filename)
                if not df.empty:
                    count = len(df)
                    print(f"Successfully saved {count} new jobs to {new_filename}")
                    
                    # Send notification
                    send_notification(
                        title="New Jobs Found!",
                        message=f"Found {count} new job postings"
                    )
                else:
                    print("New jobs were found but filtered out (older than 7 days).")
                    os.remove(new_filename) # Clean up empty file
            except:
                pass
        else:
            print("No jobs saved (likely all filtered out).")
        
    else:
        print("No new jobs found since last run.")

if __name__ == "__main__":
    main()
