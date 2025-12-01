from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
from backend.database import get_db, JobPost, AgentLog, Config, init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Job Portal API")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

# --- Pydantic Schemas ---
class JobPostSchema(BaseModel):
    id: int
    title: str
    company: str
    location: str
    link: str
    posted_date: Optional[date]
    salary: str
    match_score: int
    match_reasoning: Optional[str]
    is_applied: bool
    user_remarks: Optional[str]
    user_feedback_comment: Optional[str]
    source: str
    is_external: bool
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class JobUpdateSchema(BaseModel):
    is_applied: Optional[bool] = None
    user_remarks: Optional[str] = None
    user_feedback_comment: Optional[str] = None

class ExternalJobSchema(BaseModel):
    url: str

class LogSchema(BaseModel):
    timestamp: datetime
    agent_name: str
    message: str
    status: str

    class Config:
        orm_mode = True

class ConfigSchema(BaseModel):
    key: str
    value: Optional[str] = ""

    class Config:
        orm_mode = True

# --- Endpoints ---

@app.get("/jobs", response_model=List[JobPostSchema])
def get_jobs(db: Session = Depends(get_db)):
    # Sort by match_score DESC, then posted_date DESC
    return db.query(JobPost).order_by(JobPost.match_score.desc(), JobPost.posted_date.desc()).all()

@app.patch("/jobs/{job_id}", response_model=JobPostSchema)
def update_job(job_id: int, update_data: JobUpdateSchema, db: Session = Depends(get_db)):
    job = db.query(JobPost).filter(JobPost.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if update_data.is_applied is not None:
        job.is_applied = update_data.is_applied
    if update_data.user_remarks is not None:
        job.user_remarks = update_data.user_remarks
    if update_data.user_feedback_comment is not None:
        job.user_feedback_comment = update_data.user_feedback_comment
    
    db.commit()
    db.refresh(job)
    return job

@app.post("/jobs/external")
def add_external_job(job_data: ExternalJobSchema, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Create initial record
    new_job = JobPost(
        title="External Job (Pending Scrape)",
        company="Unknown",
        location="Unknown",
        link=job_data.url,
        posted_date_text="Today",
        posted_date=datetime.now().date(),
        salary="N/A",
        applicants="N/A",
        job_type="N/A",
        source="External",
        is_external=True,
        match_score=0,
        match_reasoning="Pending evaluation",
        created_at=datetime.now()
    )
    try:
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        # Trigger background processing
        from agents.external_processor import ExternalJobProcessor
        processor = ExternalJobProcessor()
        background_tasks.add_task(processor.process_job, new_job.id, job_data.url)
        
        return {"message": "Job added and processing started", "id": new_job.id}
    except Exception as e:
        db.rollback()
        print(f"Error adding external job: {e}") # Log to console
        if "UNIQUE constraint failed" in str(e) or "IntegrityError" in str(e):
             raise HTTPException(status_code=400, detail="Job with this link already exists.")
        raise HTTPException(status_code=400, detail=f"Error adding job: {str(e)}")

@app.delete("/jobs")
def delete_jobs(job_ids: List[int], db: Session = Depends(get_db)):
    try:
        db.query(JobPost).filter(JobPost.id.in_(job_ids)).delete(synchronize_session=False)
        db.commit()
        return {"message": f"Deleted {len(job_ids)} jobs"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs/{job_id}/analyze_feedback")
def analyze_feedback(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPost).filter(JobPost.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.user_feedback_comment:
        return {"message": "No feedback to analyze"}

    # Call LLM to analyze feedback
    from utils.llm_client import get_llm_response
    prompt = f"""
    The user provided feedback on a job recommendation.
    
    Job: {job.title} at {job.company}
    Current Reasoning: {job.match_reasoning}
    
    User Feedback: {job.user_feedback_comment}
    
    Task:
    1. Analyze the user's feedback.
    2. Update the reasoning to incorporate this feedback.
    3. If the feedback is positive (thumbs up/positive text), explain why it fits better.
    4. If negative, explain why it might not be a fit despite the score.
    
    Output ONLY the new reasoning text.
    """
    
    new_reasoning = get_llm_response(prompt)
    if new_reasoning:
        job.match_reasoning = new_reasoning.strip()
        db.commit()
        return {"message": "Reasoning updated", "new_reasoning": new_reasoning}
    
    raise HTTPException(status_code=500, detail="Failed to generate analysis")

@app.delete("/logs")
def clear_logs(db: Session = Depends(get_db)):
    try:
        db.query(AgentLog).delete()
        db.commit()
        return {"message": "Logs cleared"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs", response_model=List[LogSchema])
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(AgentLog).order_by(AgentLog.timestamp.desc()).limit(limit).all()

@app.get("/config", response_model=List[ConfigSchema])
def get_config(db: Session = Depends(get_db)):
    return db.query(Config).all()

@app.post("/config")
def update_config(config: ConfigSchema, db: Session = Depends(get_db)):
    print(f"Received config update: {config}")
    try:
        existing = db.query(Config).filter(Config.key == config.key).first()
        if existing:
            existing.value = config.value
            print(f"Updated existing key: {config.key}")
        else:
            new_config = Config(key=config.key, value=config.value)
            db.add(new_config)
            print(f"Added new key: {config.key}")
        db.commit()
        return {"message": "Config updated"}
    except Exception as e:
        print(f"Error updating config: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/bulk")
def update_config_bulk(configs: List[ConfigSchema], db: Session = Depends(get_db)):
    print(f"Received bulk config update: {len(configs)} items")
    try:
        for config in configs:
            existing = db.query(Config).filter(Config.key == config.key).first()
            if existing:
                existing.value = config.value
            else:
                new_config = Config(key=config.key, value=config.value)
                db.add(new_config)
        db.commit()
        return {"message": "Bulk config updated"}
    except Exception as e:
        print(f"Error updating bulk config: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import BackgroundTasks
from agents.orchestrator import OrchestratorAgent

orchestrator = OrchestratorAgent()

# Global State for Scraper Status
scraper_status = {
    "state": "IDLE", # IDLE, RUNNING, ERROR
    "last_run": None,
    "message": ""
}

@app.get("/status")
def get_status():
    return scraper_status

@app.post("/run")
def trigger_run(background_tasks: BackgroundTasks):
    if scraper_status["state"] == "RUNNING":
        raise HTTPException(status_code=400, detail="Scraper is already running")
    
    scraper_status["state"] = "RUNNING"
    scraper_status["message"] = "Starting scraper..."
    scraper_status["last_run"] = datetime.now()
    
    background_tasks.add_task(run_orchestrator_wrapper)
    return {"message": "Scraper run triggered in background"}

def run_orchestrator_wrapper():
    try:
        scraper_status["message"] = "Scraper running..."
        orchestrator.run_cycle()
        scraper_status["state"] = "IDLE"
        scraper_status["message"] = "Run complete"
    except Exception as e:
        scraper_status["state"] = "ERROR"
        scraper_status["message"] = f"Error: {str(e)}"
        print(f"Orchestrator Error: {e}")

# --- Persona Management ---
import json
import os

PERSONA_FILE = "success_persona.json"

@app.get("/persona")
def get_persona():
    """Get the current success persona"""
    try:
        if os.path.exists(PERSONA_FILE):
            with open(PERSONA_FILE, 'r') as f:
                persona = json.load(f)
            return persona
        else:
            return {"error": "Persona file not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading persona: {str(e)}")

@app.post("/persona")
def update_persona(persona: dict):
    """Update the success persona"""
    try:
        with open(PERSONA_FILE, 'w') as f:
            json.dump(persona, f, indent=4)
        return {"message": "Persona updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating persona: {str(e)}")
