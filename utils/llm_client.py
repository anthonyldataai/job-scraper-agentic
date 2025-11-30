import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def get_llm_response(prompt: str, model_name: str = "gemini-2.0-flash") -> Optional[str]:
    """
    Generates a response from the Google Gemini model.
    Uses gemini-2.0-flash by default for higher rate limits.
    """
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not set.")
        return None

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"LLM Rate Limit: Waiting 2 seconds and retrying with gemini-2.0-flash...")
            import time
            time.sleep(2)
            # Retry with stable model
            try:
                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content(prompt)
                return response.text
            except Exception as retry_error:
                print(f"LLM Retry Error: {retry_error}")
                return None
        else:
            print(f"LLM Error: {e}")
            return None

def clean_json_response(response_text: str) -> str:
    """
    Cleans markdown code blocks from LLM JSON response.
    """
    if not response_text:
        return ""
    return response_text.replace("```json", "").replace("```", "").strip()
