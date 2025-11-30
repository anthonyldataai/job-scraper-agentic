import schedule
import time
import asyncio
import pandas as pd
import os
from datetime import datetime
from job_scraper import scrape_all_jobs
from agents.learner import LearnerAgent
from agents.validator import ValidatorAgent
from agents.corrector import SelfCorrectorAgent
from agents.evaluator import EvaluatorAgent
from utils.persistence import log_agent_action, get_config_value
from backend.database import SessionLocal, JobPost, Config

class OrchestratorAgent:
    def __init__(self):
        self.learner = LearnerAgent()
        self.validator = ValidatorAgent()
        self.corrector = SelfCorrectorAgent()
        self.evaluator = EvaluatorAgent()

    def initialize(self):
        log_agent_action("Orchestrator", "System initializing...", "INFO")
        # Ensure persona exists
        if not os.path.exists(self.learner.persona_file):
            self.learner.build_persona()
        else:
            log_agent_action("Orchestrator", "Success Persona loaded.", "INFO")

    def run_cycle(self):
        log_agent_action("Orchestrator", f"Starting Cycle at {datetime.now()}", "INFO")
        
        # 1. Scrape
        log_agent_action("Orchestrator", "Launching Scraper...", "INFO")
        try:
            raw_jobs = asyncio.run(scrape_all_jobs())
        except Exception as e:
            log_agent_action("Orchestrator", f"Scraper failed with error: {e}", "ERROR")
            return

        if not raw_jobs:
            log_agent_action("Orchestrator", "No jobs found this cycle.", "INFO")
            return

        # 2. Validate
        validated_jobs = self.validator.validate_jobs(raw_jobs)
        
        # 3. Self-Correction Check
        if self.validator.critical_error_flag:
            log_agent_action("Orchestrator", "Critical error detected! Handing over to Self-Corrector.", "CRITICAL")
            self.corrector.attempt_repair()
            return

        if not validated_jobs:
            log_agent_action("Orchestrator", "No jobs passed validation.", "INFO")
            return

        # 4. Deduplicate (against DB)
        new_jobs = self.deduplicate(validated_jobs)
        if not new_jobs:
            log_agent_action("Orchestrator", "All jobs already seen.", "INFO")
            return

        # 5. Score
        scored_jobs = self.evaluator.score_jobs(new_jobs)

        # 6. Save to DB
        self.save_results_to_db(scored_jobs)
        
        log_agent_action("Orchestrator", "Cycle complete.", "SUCCESS")

    def deduplicate(self, jobs):
        db = SessionLocal()
        try:
            # Get all existing links
            existing_links = {r[0] for r in db.query(JobPost.link).all()}
            
            unique_jobs = []
            # We use a set to track links we've seen in this batch + existing DB links
            seen_links = set(existing_links)
            
            for job in jobs:
                # Handle both Title Case and lowercase keys just in case
                link = job.get('Link') or job.get('link')
                
                if link:
                    link = link.strip()
                    if link not in seen_links:
                        unique_jobs.append(job)
                        seen_links.add(link)
            
            return unique_jobs
        finally:
            db.close()

    def save_results_to_db(self, jobs):
        db = SessionLocal()
        count = 0
        try:
            for job_data in jobs:
                # Convert date if needed
                posted_date = job_data.get('Posted Date')
                if isinstance(posted_date, datetime):
                    posted_date = posted_date.date()
                
                new_job = JobPost(
                    title=job_data.get('Title'),
                    company=job_data.get('Company'),
                    location=job_data.get('Location'),
                    link=job_data.get('Link'),
                    posted_date_text=job_data.get('Posted Date Text'),
                    posted_date=posted_date,
                    salary=job_data.get('Salary'),
                    applicants=job_data.get('Applicants'),
                    job_type=job_data.get('Job Type'),
                    source=job_data.get('Source'),
                    match_score=job_data.get('match_score', 0),
                    match_reasoning=job_data.get('match_reasoning', ""),
                    is_external=False
                )
                db.add(new_job)
                count += 1
            db.commit()
            log_agent_action("Orchestrator", f"{count} new leads saved to Database.", "SUCCESS")
        except Exception as e:
            db.rollback()
            log_agent_action("Orchestrator", f"Error saving to DB: {e}", "ERROR")
        finally:
            db.close()

    def start_schedule(self):
        log_agent_action("Orchestrator", "Scheduler started.", "INFO")
        
        # Run once immediately
        self.run_cycle()
        
        while True:
            # Dynamic Interval Check
            interval_minutes = int(get_config_value("schedule_interval", "30"))
            log_agent_action("Orchestrator", f"Next run in {interval_minutes} minutes.", "INFO")
            
            # We sleep in short bursts to check for config changes or stop signals
            # But for simplicity here, we just sleep the full duration or check every minute
            for _ in range(interval_minutes):
                time.sleep(60)
                # Check if we are in allowed hours (09:00 - 21:00)
                now = datetime.now()
                if not (9 <= now.hour < 21):
                    continue 

            self.run_cycle_if_in_hours()

    def run_cycle_if_in_hours(self):
        now = datetime.now()
        if 9 <= now.hour < 21:
            self.run_cycle()
        else:
            log_agent_action("Orchestrator", f"Skipping run (outside 09:00-21:00 window). Current time: {now}", "INFO")

if __name__ == "__main__":
    orchestrator = OrchestratorAgent()
    orchestrator.initialize()
    # For testing purposes, we run one cycle. 
    # In production, we would call start_schedule()
    orchestrator.run_cycle()
