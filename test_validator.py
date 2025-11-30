import json
from agents.validator import ValidatorAgent

# Sample job list with minimal fields (only Title and Source)
jobs = [{
    "Title": "Senior Mechanical Engineer",
    "Source": "LinkedIn"
}]

validator = ValidatorAgent()
valid_jobs = validator.validate_jobs(jobs)
print('Valid jobs count:', len(valid_jobs))
print('Valid jobs:', json.dumps(valid_jobs, indent=2))
