import os
import shutil
import json
from datetime import datetime
from utils.llm_client import get_llm_response, clean_json_response
from utils.persistence import load_json, clear_error_counter, ERROR_TRACKER_FILE, log_agent_action

SCRAPER_FILE = "job_scraper.py"

class SelfCorrectorAgent:
    def __init__(self):
        pass

    def attempt_repair(self):
        log_agent_action("Self-Corrector", "CRITICAL error hit 3/3. Initiating repair protocol...", "CRITICAL")
        
        # 1. Read Error Logs
        tracker = load_json(ERROR_TRACKER_FILE)
        if not tracker:
            log_agent_action("Self-Corrector", "No error logs found. Aborting.", "ERROR")
            return

        critical_error = max(tracker.items(), key=lambda x: x[1]['count'])
        error_type, error_data = critical_error
        error_details = "\n".join(error_data['details'])
        
        print(f"SELF-CORRECTOR: Analyzing error pattern: {error_type}")

        # 2. Read Code
        if not os.path.exists(SCRAPER_FILE):
            print(f"SELF-CORRECTOR: {SCRAPER_FILE} not found!")
            return
            
        with open(SCRAPER_FILE, 'r', encoding='utf-8') as f:
            code_content = f.read()

        # 3. Prompt LLM for Analysis & Fix
        prompt = f"""
        You are an expert Python developer and web scraping specialist.
        The following Python script has encountered a critical repeated error.
        
        Error Type: {error_type}
        Recent Error Details:
        {error_details}
        
        Source Code:
        ```python
        {code_content}
        ```
        
        Task:
        1. Analyze the code and the error to identify the root cause.
        2. Propose a fix by rewriting the ENTIRE script.
        3. Assess the risks of this fix (e.g., side effects, breaking other scrapers).
        
        Output a JSON object with this structure:
        {{
            "analysis": "Explanation of the bug...",
            "risk_assessment": "Potential negative consequences...",
            "fixed_code": "The full python code..."
        }}
        """
        
        print("SELF-CORRECTOR: Requesting analysis and fix from LLM...")
        response = get_llm_response(prompt, model_name="gemini-2.0-flash-exp")
        
        if response:
            try:
                result = json.loads(clean_json_response(response))
                analysis = result.get("analysis", "No analysis provided.")
                risks = result.get("risk_assessment", "No risk assessment provided.")
                fixed_code = result.get("fixed_code", "")
                
                if not fixed_code or len(fixed_code) < 100:
                    print("SELF-CORRECTOR: LLM returned invalid code. Aborting.")
                    return

                # 4. Human-in-the-loop Approval
                print("\n" + "="*50)
                print("SELF-CORRECTOR: PROPOSED FIX")
                print("="*50)
                print(f"Analysis: {analysis}")
                print(f"Risk Assessment: {risks}")
                print("-" * 50)
                
                # In a real scheduled service, we might save this to a file and notify the user.
                # For this implementation, we ask via input (assuming interactive run) or auto-skip if headless.
                # We'll assume interactive for now as per user request.
                
                user_input = input("Do you want to apply this fix? (yes/no): ").lower().strip()
                
                if user_input == 'yes' or user_input == 'y':
                    # 5. Backup and Overwrite
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_file = f"{SCRAPER_FILE}.{timestamp}.bak"
                    shutil.copy(SCRAPER_FILE, backup_file)
                    print(f"SELF-CORRECTOR: Backup created at {backup_file}")
                    
                    with open(SCRAPER_FILE, 'w', encoding='utf-8') as f:
                        f.write(fixed_code)
                    
                    print(f"SELF-CORRECTOR: {SCRAPER_FILE} has been successfully rewritten and deployed.")
                    
                    # 6. Clear Error Counter
                    clear_error_counter(error_type)
                    print("SELF-CORRECTOR: Error counter reset.")
                else:
                    print("SELF-CORRECTOR: Fix rejected by user. No changes made.")
                    
            except Exception as e:
                print(f"SELF-CORRECTOR: Error parsing LLM response: {e}")
        else:
            print("SELF-CORRECTOR: Failed to get fix from LLM.")
