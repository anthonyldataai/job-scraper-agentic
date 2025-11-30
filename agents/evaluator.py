import json
from typing import List, Dict, Any
from utils.persistence import load_json, SUCCESS_PERSONA_FILE, log_agent_action
from utils.llm_client import get_llm_response, clean_json_response

class EvaluatorAgent:
    def __init__(self):
        self.persona = load_json(SUCCESS_PERSONA_FILE)

    def score_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.persona:
            log_agent_action("Evaluator", "No Success Persona found. Skipping scoring.", "WARNING")
            return jobs
            
        log_agent_action("Evaluator", f"Scoring {len(jobs)} jobs against persona...", "INFO")
        
        # Batch scoring to reduce API calls and avoid rate limits
        scored_jobs = []
        batch_size = 5
        
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            batch_results = self.evaluate_batch(batch)
            
            for job, (score, reasoning) in zip(batch, batch_results):
                job['match_score'] = score
                job['match_reasoning'] = reasoning
                scored_jobs.append(job)
            
        # Sort by score
        scored_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        if scored_jobs:
            highest = scored_jobs[0].get('match_score', 0)
            log_agent_action("Evaluator", f"Scored {len(scored_jobs)} jobs. Highest score: {highest}.", "SUCCESS")
            
        return scored_jobs
    
    def evaluate_batch(self, jobs: List[Dict[str, Any]]):
        """Evaluate a batch of jobs in a single LLM call"""
        jobs_text = "\n\n".join([
            f"Job {i+1}:\nTitle: {job.get('Title')}\nCompany: {job.get('Company')}\nLocation: {job.get('Location')}\nSalary: {job.get('Salary')}\nType: {job.get('Job Type')}"
            for i, job in enumerate(jobs)
        ])
        
        prompt = f"""
        Evaluate these job postings against the candidate's Success Persona.
        
        Persona:
        {json.dumps(self.persona, indent=2)}
        
        Jobs:
        {jobs_text}
        
        Task:
        For each job, provide a score from 0 to 100 based on the persona's scoring rubric and brief reasoning.
        
        Output JSON array:
        [
            {{"job_number": 1, "score": 85, "reasoning": "Matches core skills..."}},
            {{"job_number": 2, "score": 60, "reasoning": "Location not ideal..."}}
        ]
        """
        
        response = get_llm_response(prompt)
        if response:
            try:
                results = json.loads(clean_json_response(response))
                return [(r.get("score", 0), r.get("reasoning", "No reasoning provided.")) for r in results]
            except:
                pass
        
        # Fallback: return default scores
        return [(50, "Error evaluating job.") for _ in jobs]

    def evaluate_single_job(self, job: Dict[str, Any]):
        prompt = f"""
        Evaluate this job posting against the candidate's Success Persona.
        
        Persona:
        {json.dumps(self.persona, indent=2)}
        
        Job:
        Title: {job.get('Title')}
        Company: {job.get('Company')}
        Location: {job.get('Location')}
        Salary: {job.get('Salary')}
        Type: {job.get('Job Type')}
        
        Task:
        1. Score the job from 0 to 100 based on the persona's scoring rubric.
        2. Provide a brief reasoning (1-2 sentences).
        
        Output JSON:
        {{
            "score": 85,
            "reasoning": "Matches core skills and industry, but location is not ideal."
        }}
        """
        
        response = get_llm_response(prompt)
        if response:
            try:
                data = json.loads(clean_json_response(response))
                return data.get("score", 0), data.get("reasoning", "No reasoning provided.")
            except:
                pass
        
        return 0, "Error evaluating job."
