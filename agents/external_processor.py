import asyncio
from playwright.async_api import async_playwright
from agents.evaluator import EvaluatorAgent
from utils.persistence import log_agent_action
from backend.database import SessionLocal, JobPost
from datetime import datetime

class ExternalJobProcessor:
    def __init__(self):
        self.evaluator = EvaluatorAgent()

    async def process_job(self, job_id: int, url: str):
        log_agent_action("ExternalProcessor", f"Starting processing for job {job_id}: {url}", "INFO")
        
        db = SessionLocal()
        job = db.query(JobPost).filter(JobPost.id == job_id).first()
        if not job:
            log_agent_action("ExternalProcessor", f"Job {job_id} not found in DB", "ERROR")
            db.close()
            return

        try:
            # 1. Scrape Content
            log_agent_action("ExternalProcessor", "Scraping page content...", "INFO")
            content = await self._scrape_content(url)
            
            if not content:
                log_agent_action("ExternalProcessor", "Failed to scrape content", "ERROR")
                job.match_reasoning = "Failed to scrape content from URL."
                db.commit()
                return

            # 2. Update Job Details (Basic extraction could be improved with LLM)
            # For now, we'll put the raw content in description or just use it for evaluation
            # We will try to extract a title if possible, otherwise keep "External Job"
            
            # 3. Evaluate
            log_agent_action("ExternalProcessor", "Evaluating job against persona...", "INFO")
            
            # Create a temporary job dict for the evaluator
            job_dict = {
                "id": job.id,
                "title": job.title, # Evaluator might use this
                "company": job.company,
                "description": content, # Important: Pass full content
                "link": url,
                "source": "External"
            }
            
            # We need to adapt Evaluator to take a single job or just use its internal logic
            # The current Evaluator processes a batch from DB. 
            # Let's use a direct LLM call here for simplicity and speed, 
            # or reuse the Evaluator's core logic if exposed.
            
            # Reusing Evaluator's _evaluate_job_batch logic is hard because it expects a list.
            # Let's call the LLM directly using the same prompt style.
            
            from utils.llm_client import get_llm_response
            from agents.learner import LearnerAgent
            
            learner = LearnerAgent()
            persona = learner.get_persona()
            
            prompt = f"""
            You are a Career Agent evaluating a job posting against a user's success persona.
            
            User Persona:
            {persona}
            
            Job Posting Content:
            {content[:10000]}  # Truncate to avoid token limits
            
            Task:
            1. Extract the Job Title and Company Name if possible.
            2. Evaluate the match score (0-100).
            3. Provide a concise reasoning.
            
            Output JSON:
            {{
                "title": "Extracted Title",
                "company": "Extracted Company",
                "match_score": 85,
                "match_reasoning": "Reasoning here..."
            }}
            """
            
            response = get_llm_response(prompt)
            
            if response:
                import json
                try:
                    # Clean response if needed (remove markdown)
                    clean_resp = response.replace('```json', '').replace('```', '')
                    data = json.loads(clean_resp)
                    
                    job.title = data.get("title", job.title)
                    job.company = data.get("company", job.company)
                    job.match_score = data.get("match_score", 0)
                    job.match_reasoning = data.get("match_reasoning", "Evaluated by AI")
                    
                    log_agent_action("ExternalProcessor", f"Evaluation complete. Score: {job.match_score}", "SUCCESS")
                    
                except json.JSONDecodeError:
                    log_agent_action("ExternalProcessor", "Failed to parse LLM response", "ERROR")
                    job.match_reasoning = "Error parsing evaluation results."
            else:
                log_agent_action("ExternalProcessor", "No response from LLM", "ERROR")
            
            db.commit()

        except Exception as e:
            log_agent_action("ExternalProcessor", f"Error processing job: {e}", "ERROR")
        finally:
            db.close()

    async def _scrape_content(self, url: str):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                # Get text content
                text = await page.evaluate("document.body.innerText")
                return text
            except Exception as e:
                print(f"Scrape error: {e}")
                return None
            finally:
                await browser.close()
