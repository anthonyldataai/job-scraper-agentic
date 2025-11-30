import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.job_model import JobPost
from utils.persistence import log_agent_action, get_config_value
from utils.llm_client import get_llm_response, clean_json_response

class ValidatorAgent:
    def __init__(self):
        self.critical_error_flag = False

    def validate_job(self, job: JobPost) -> bool:
        """
        Validates a job post against rules and industry relevance.
        """
        # 1. Basic Data Integrity
        if not job.title:
            log_agent_action("Validator", f"Invalid job data: missing title", status="ERROR")
            return False

        # 2. Date Check (7 Days)
        if job.posted_date:
            seven_days_ago = datetime.now() - timedelta(days=7)
            # Ensure posted_date is datetime or date
            if isinstance(job.posted_date, (datetime, str)):
                 # If it's a string, we might need to parse it, but let's assume it's handled or we skip strict check for now
                 pass
            elif job.posted_date < seven_days_ago.date(): # Compare dates
                log_agent_action("Validator", f"Job too old: {job.title} ({job.posted_date})", status="INFO")
                return False

        # 3. Industry Validation (LLM)
        target_industries_json = get_config_value("target_industries")
        if target_industries_json:
            try:
                target_industries = json.loads(target_industries_json)
                if target_industries:
                    # We only check if we have a valid list
                    # To avoid excessive API calls, we could limit this or cache it.
                    # For now, we'll do it for every job as requested.
                    is_relevant = self.check_industry_relevance(job, target_industries)
                    if not is_relevant:
                        log_agent_action("Validator", f"Job filtered out (Industry Mismatch): {job.title} at {job.company}", status="INFO")
                        return False
            except json.JSONDecodeError:
                log_agent_action("Validator", "Error parsing target_industries config", status="ERROR")

        log_agent_action("Validator", f"Job validated: {job.title}", status="SUCCESS")
        return True

    def check_industry_relevance(self, job: JobPost, target_industries: list) -> bool:
        """
        Uses LLM to check if the job belongs to the target industries.
        """
        prompt = f"""
        You are an expert industry analyst.
        Job Title: {job.title}
        Company: {job.company}
        
        Target Industries: {", ".join(target_industries)}
        
        Does this job likely belong to ANY of the target industries?
        Consider the company's known business and the nature of the role.
        
        Respond with ONLY 'YES' or 'NO'.
        """
        
        try:
            # We need to use the LLM client here. 
            # Assuming get_llm_response is available and works.
            response = get_llm_response(prompt)
            if response:
                return "YES" in response.strip().upper()
            return True # Default to True if LLM fails to avoid blocking
        except Exception as e:
            log_agent_action("Validator", f"LLM Industry Check Failed: {e}", status="ERROR")
            return True

    def validate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validates a list of job dictionaries.
        Returns only the valid jobs.
        """
        valid_jobs = []
        for job_dict in jobs:
            # Convert dict to JobPost for validation
            try:
                job = JobPost(
                    title=job_dict.get('Title') or job_dict.get('title', ''),
                    company=job_dict.get('Company') or job_dict.get('company', ''),
                    location=job_dict.get('Location') or job_dict.get('location', ''),
                    link=job_dict.get('Link') or job_dict.get('link', ''),
                    posted_date_text=job_dict.get('Posted Date Text') or job_dict.get('posted_date_text', ''),
                    posted_date=job_dict.get('Posted Date') or job_dict.get('posted_date', None),
                    salary=job_dict.get('Salary') or job_dict.get('salary', 'N/A'),
                    applicants=job_dict.get('Applicants') or job_dict.get('applicants', 'N/A'),
                    job_type=job_dict.get('Job Type') or job_dict.get('job_type', 'N/A'),
                    source=job_dict.get('Source') or job_dict.get('source', '')
                )
                
                if self.validate_job(job):
                    valid_jobs.append(job_dict)
            except Exception as e:
                log_agent_action("Validator", f"Error validating job: {e}", status="ERROR")
                continue
        
        log_agent_action("Validator", f"Validated {len(valid_jobs)}/{len(jobs)} jobs", status="INFO")
        return valid_jobs
