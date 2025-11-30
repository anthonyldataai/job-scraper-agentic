import json
import os
from datetime import datetime
from typing import Dict, Any
from backend.database import SessionLocal, AgentLog, Config, JobPost

# Keep file-based persistence for complex objects like Persona and Error Tracker for now
# We could migrate these to DB later, but for now, let's focus on Logs and Jobs
ERROR_TRACKER_FILE = "error_tracker.json"
SUCCESS_PERSONA_FILE = "success_persona.json"

def load_json(filename: str) -> Dict[str, Any]:
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return {}

def save_json(filename: str, data: Dict[str, Any]):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, default=str)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

# --- Database Logging ---

def log_agent_action(agent_name: str, message: str, status: str = "INFO"):
    """Logs an agent action to the database."""
    print(f"[{agent_name}] {message}") # Keep stdout for debugging
    
    db = SessionLocal()
    try:
        log_entry = AgentLog(
            agent_name=agent_name,
            message=message,
            status=status,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        print(f"DB Log Error: {e}")
    finally:
        db.close()

# --- Error Tracking (Hybrid: DB Log + File Tracker) ---

def log_error(error_type: str, details: str):
    # Log to DB
    log_agent_action("System", f"Error: {error_type} - {details}", "ERROR")
    
    # Update File Tracker (for Self-Corrector logic which relies on counts)
    tracker = load_json(ERROR_TRACKER_FILE)
    
    if error_type not in tracker:
        tracker[error_type] = {"count": 0, "first_seen": datetime.now(), "last_seen": datetime.now(), "details": []}
    
    tracker[error_type]["count"] += 1
    tracker[error_type]["last_seen"] = datetime.now()
    tracker[error_type]["details"].append(details)
    
    # Keep only last 5 details
    tracker[error_type]["details"] = tracker[error_type]["details"][-5:]
    
    save_json(ERROR_TRACKER_FILE, tracker)
    return tracker[error_type]["count"]

def clear_error_counter(error_type: str):
    tracker = load_json(ERROR_TRACKER_FILE)
    if error_type in tracker:
        tracker[error_type]["count"] = 0
        save_json(ERROR_TRACKER_FILE, tracker)

def get_error_count(error_type: str) -> int:
    tracker = load_json(ERROR_TRACKER_FILE)
    return tracker.get(error_type, {}).get("count", 0)

# --- Config Management ---

def get_config_value(key: str, default: str = None) -> str:
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == key).first()
        return config.value if config else default
    finally:
        db.close()

def set_config_value(key: str, value: str):
    db = SessionLocal()
    try:
        config = db.query(Config).filter(Config.key == key).first()
        if config:
            config.value = value
        else:
            new_config = Config(key=key, value=value)
            db.add(new_config)
        db.commit()
    finally:
        db.close()
