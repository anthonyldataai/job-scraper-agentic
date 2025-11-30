from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime

class JobPost(BaseModel):
    title: str = Field("", alias="Title")
    company: str = Field("", alias="Company")
    location: str = Field("", alias="Location")
    link: str = Field("", alias="Link")
    posted_date_text: str = Field("", alias="Posted Date Text")
    posted_date: Optional[datetime] = Field(None, alias="Posted Date")
    salary: str = Field("N/A", alias="Salary")
    applicants: str = Field("N/A", alias="Applicants")
    job_type: str = Field("N/A", alias="Job Type")
    apply_method: str = Field("Apply", alias="Apply Method")
    source: str = Field("", alias="Source")
    
    # Internal fields for the system
    match_score: int = Field(0, description="Score from 0-100 based on persona")
    match_reasoning: str = Field("", description="Reasoning for the score")
    is_validated: bool = Field(False, description="Has passed validation")
    
    # User Interaction
    is_applied: bool = Field(False)
    user_remarks: Optional[str] = None
    user_feedback_comment: Optional[str] = None
    is_external: bool = Field(False)

    class Config:
        populate_by_name = True

class SuccessPersona(BaseModel):
    keywords: List[str]
    preferred_industries: List[str]
    avoid_keywords: List[str]
    experience_level: str
    core_skills: List[str]
    cultural_fit: str
    scoring_rubric: str

class ErrorLog(BaseModel):
    timestamp: datetime
    error_type: str
    details: str
    count: int = 1
