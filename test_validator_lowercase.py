import json
from agents.validator import ValidatorAgent

# Sample job list with lowercase keys (simulating the user's error case)
jobs = [{
    "title": "Senior Mechanical Engineer",
    "source": "LinkedIn"
}]

validator = ValidatorAgent()
valid_jobs = validator.validate_jobs(jobs)
print('Valid jobs count:', len(valid_jobs))
print('Valid jobs:', json.dumps(valid_jobs, indent=2))
