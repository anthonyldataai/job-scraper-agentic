import os
import glob
import json
from utils.llm_client import get_llm_response, clean_json_response
from utils.persistence import save_json, load_json, SUCCESS_PERSONA_FILE, log_agent_action
from backend.database import SessionLocal, JobPost

class LearnerAgent:
    def __init__(self):
        self.cv_dir = "CV"
        self.interview_dir = "Job Interview"
        self.persona_file = SUCCESS_PERSONA_FILE

    def read_files(self, directory):
        content = ""
        if not os.path.exists(directory):
            log_agent_action("Learner", f"Directory {directory} not found.", "WARNING")
            return ""
            
        files = glob.glob(os.path.join(directory, "*"))
        for f in files:
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                    content += f"\n--- File: {os.path.basename(f)} ---\n"
                    content += file.read()
            except Exception as e:
                log_agent_action("Learner", f"Error reading {f}: {e}", "ERROR")
        return content

    def get_user_feedback(self):
        """Fetches user feedback from the database."""
        db = SessionLocal()
        try:
            # Get jobs with feedback comments
            jobs_with_feedback = db.query(JobPost).filter(JobPost.user_feedback_comment.isnot(None)).all()
            if not jobs_with_feedback:
                return ""
            
            feedback_text = "\n--- User Feedback on Past Jobs ---\n"
            for job in jobs_with_feedback:
                feedback_text += f"Job: {job.title} at {job.company}\n"
                feedback_text += f"Score: {job.match_score}\n"
                feedback_text += f"User Feedback: {job.user_feedback_comment}\n"
                feedback_text += "---\n"
            
            return feedback_text
        except Exception as e:
            log_agent_action("Learner", f"Error fetching feedback: {e}", "ERROR")
            return ""
        finally:
            db.close()

    def build_persona(self):
        log_agent_action("Learner", "Initializing. Reading context files...", "INFO")
        
        cv_content = self.read_files(self.cv_dir)
        interview_content = self.read_files(self.interview_dir)
        feedback_content = self.get_user_feedback()
        
        if not cv_content and not interview_content:
            log_agent_action("Learner", "No context files found. Cannot build persona.", "ERROR")
            return None

        prompt = f"""
        You are an expert career coach and AI analyst. 
        Analyze the following CVs, Job Interview notes, and User Feedback to create/refine a "Success Persona" for this candidate.
        
        This persona will be used to score new job postings.
        
        CV Content:
        {cv_content[:10000]} 
        
        Interview Content:
        {interview_content[:10000]}
        
        User Feedback History (CRITICAL: Adjust persona based on this):
        {feedback_content}
        
        Output a JSON object with the following structure:
        {{
            "keywords": ["list", "of", "important", "keywords"],
            "preferred_industries": ["list", "of", "industries"],
            "avoid_keywords": ["list", "of", "red", "flags"],
            "experience_level": "Senior/Mid/Junior etc",
            "core_skills": ["list", "of", "skills"],
            "cultural_fit": "Description of ideal culture",
            "scoring_rubric": "A detailed instruction on how to score a job from 0-100 based on this persona."
        }}
        """
        
        log_agent_action("Learner", "Generating Success Persona using LLM...", "INFO")
        response = get_llm_response(prompt, model_name="gemini-1.5-pro")
        
        if response:
            try:
                cleaned_json = clean_json_response(response)
                persona_data = json.loads(cleaned_json)
                save_json(self.persona_file, persona_data)
                log_agent_action("Learner", f"Success Persona established and saved to {self.persona_file}.", "SUCCESS")
                return persona_data
            except Exception as e:
                log_agent_action("Learner", f"Error parsing LLM response: {e}", "ERROR")
                return None
        else:
            log_agent_action("Learner", "Failed to get LLM response.", "ERROR")
            return None

    def get_persona(self):
        """Loads the persona from the file."""
        if os.path.exists(self.persona_file):
            return load_json(self.persona_file)
        return None

if __name__ == "__main__":
    agent = LearnerAgent()
    agent.build_persona()
