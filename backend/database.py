
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./job_portal.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class JobPost(Base):
    __tablename__ = "job_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    link = Column(String, unique=True, index=True)
    posted_date_text = Column(String)
    posted_date = Column(Date, nullable=True)
    salary = Column(String)
    applicants = Column(String)
    job_type = Column(String)
    source = Column(String)
    
    # AI Scoring
    match_score = Column(Integer, default=0)
    match_reasoning = Column(Text)
    
    # User Interaction
    is_applied = Column(Boolean, default=False)
    user_remarks = Column(Text, nullable=True)
    user_feedback_comment = Column(Text, nullable=True) # For Learner Agent
    is_external = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String)
    message = Column(Text)
    status = Column(String) # "INFO", "SUCCESS", "ERROR", "CRITICAL"

class Config(Base):
    __tablename__ = "config"

    key = Column(String, primary_key=True, index=True)
    value = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Initialize default config if not exists
    defaults = {
        "keywords": '["Technical Project Manager", "Product Owner"]',
        "location": "London",
        "schedule_interval": "30",
        "target_industries": '["FinTech", "Capital Markets", "Asset Management", "Security Brokers", "Fund House", "Investment Banking"]'
    }
    
    for key, value in defaults.items():
        if not db.query(Config).filter_by(key=key).first():
            db.add(Config(key=key, value=value))
    
    db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
