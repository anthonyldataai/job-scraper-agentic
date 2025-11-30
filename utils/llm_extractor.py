"""
LLM-based job data extraction utility.
Uses Gemini to intelligently parse job posting content.
"""
import json
from utils.llm_client import get_llm_response

async def extract_job_details_with_llm(page_content: str, job_url: str) -> dict:
    """
    Uses LLM to extract structured job information from raw page content.
    
    Args:
        page_content: Raw HTML or text content from job posting page
        job_url: URL of the job posting (for context)
    
    Returns:
        dict with keys: title, company, salary, location, posted_date, job_type, description
    """
    
    prompt = f"""You are a job data extraction expert. Analyze the following job posting content and extract key information.

Job URL: {job_url}

Page Content (HTML/Text):
{page_content[:8000]}  

Extract the following information in JSON format:
{{
    "title": "Job title",
    "company": "Company name",
    "salary": "Salary information (e.g., '£50,000 - £60,000', 'Up to £600 per day', 'Negotiable', 'Competitive')",
    "location": "Job location",
    "posted_date": "When the job was posted (e.g., '1 day ago', 'Yesterday', '2 weeks ago')",
    "job_type": "Employment type (e.g., 'Permanent', 'Contract', 'Temporary')",
    "description_summary": "Brief 2-3 sentence summary of the role"
}}

Rules:
- If a field cannot be found, use "N/A"
- For salary, include the full range if available
- For posted_date, extract the relative time phrase (e.g., "published: 1 day ago" → "1 day ago")
- Be precise and extract exactly what you see
- Return ONLY valid JSON, no additional text

JSON:"""

    try:
        response = get_llm_response(prompt)
        
        # Extract JSON from response
        # Sometimes LLM adds markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        data = json.loads(response)
        
        # Ensure all required fields exist
        required_fields = ["title", "company", "salary", "location", "posted_date", "job_type"]
        for field in required_fields:
            if field not in data:
                data[field] = "N/A"
        
        return data
        
    except Exception as e:
        print(f"LLM extraction error: {e}")
        # Return default structure if LLM fails
        return {
            "title": "N/A",
            "company": "N/A",
            "salary": "N/A",
            "location": "N/A",
            "posted_date": "N/A",
            "job_type": "N/A",
            "description_summary": "N/A"
        }
