# Job Scraper Scheduling Instructions

## Overview
This document provides instructions for scheduling the job scraper to run automatically.

## Schedule Requirements

### 1. Main Scraper (Daily at 9:15 AM)
- **Script**: `run_main_scraper.bat`
- **Frequency**: Daily (including weekends)
- **Time**: 9:15 AM
- **Purpose**: Generate the master file with all jobs

### 2. Monitor Scraper (Every 30 minutes, Weekdays 9:30 AM - 9:00 PM)
- **Script**: `run_monitor.bat`
- **Frequency**: Every 30 minutes
- **Days**: Monday - Friday only
- **Time Range**: 9:30 AM to 9:00 PM
- **Purpose**: Check for new jobs and send notifications

## Setup Instructions

### Step 1: Install Notification Library
```powershell
pip install plyer
```

### Step 2: Create Task for Main Scraper (Daily 9:15 AM)

Run this command in PowerShell (as Administrator):

```powershell
schtasks /create /tn "Job Scraper - Daily Main" /tr "C:\AI\job_scraper\run_main_scraper.bat" /sc daily /st 09:15 /ru "SYSTEM"
```

### Step 3: Create Task for Monitor (Every 30 min, Weekdays 9:30 AM - 9:00 PM)

Run this command in PowerShell (as Administrator):

```powershell
schtasks /create /tn "Job Scraper - Monitor" /tr "C:\AI\job_scraper\run_monitor.bat" /sc minute /mo 30 /st 09:30 /et 21:00 /du 11:30 /k /ru "SYSTEM"
```

**Note**: The `/du 11:30` sets duration to 11 hours 30 minutes (9:30 AM to 9:00 PM). The `/k` flag terminates the task at the end time.

To restrict to weekdays only, you need to modify the task after creation:

```powershell
# First create the task, then modify it
schtasks /change /tn "Job Scraper - Monitor" /d MON,TUE,WED,THU,FRI
```

### Alternative: Using Task Scheduler GUI

1. Open **Task Scheduler** (search in Start menu)
2. Click **Create Task** (not "Create Basic Task")

#### For Main Scraper:
- **General Tab**:
  - Name: `Job Scraper - Daily Main`
  - Run whether user is logged on or not: ✓
- **Triggers Tab**:
  - New → Daily
  - Start: 9:15 AM
  - Recur every: 1 day
- **Actions Tab**:
  - New → Start a program
  - Program: `C:\AI\job_scraper\run_main_scraper.bat`
  - Start in: `C:\AI\job_scraper`

#### For Monitor:
- **General Tab**:
  - Name: `Job Scraper - Monitor`
  - Run whether user is logged on or not: ✓
- **Triggers Tab**:
  - New → On a schedule
  - Daily, Recur every: 1 day
  - Repeat task every: 30 minutes
  - For a duration of: 11 hours 30 minutes
  - Stop task if it runs longer than: 1 hour
  - Enabled: ✓
  - Advanced settings:
    - Start: 9:30 AM
    - Expire: Never
  - Days: Monday, Tuesday, Wednesday, Thursday, Friday only
- **Actions Tab**:
  - New → Start a program
  - Program: `C:\AI\job_scraper\run_monitor.bat`
  - Start in: `C:\AI\job_scraper`

## Notifications

When new jobs are found, you'll receive a Windows toast notification:
- **Title**: "New Jobs Found!"
- **Message**: "Found X new job postings"

The notification will appear in the bottom-right corner of your screen.

## Verify Tasks

To verify tasks are created:
```powershell
schtasks /query /tn "Job Scraper - Daily Main"
schtasks /query /tn "Job Scraper - Monitor"
```

## Delete Tasks (if needed)

To remove the scheduled tasks:
```powershell
schtasks /delete /tn "Job Scraper - Daily Main" /f
schtasks /delete /tn "Job Scraper - Monitor" /f
```

## Testing

To test the tasks manually:
```powershell
schtasks /run /tn "Job Scraper - Daily Main"
schtasks /run /tn "Job Scraper - Monitor"
```

## Output Files

- **Daily Main Scraper**: Creates/updates `jobs_v4.xlsx`
- **Monitor**: Creates `new_jobs_YYYYMMDD_HHMMSS.xlsx` when new jobs are found
- **Master List**: `jobs_master.xlsx` (updated by monitor)
