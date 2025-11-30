from agents.orchestrator import OrchestratorAgent
import os

def main():
    # Check for API Key
    if not os.getenv("GOOGLE_API_KEY"):
        print("CRITICAL WARNING: GOOGLE_API_KEY is not set. LLM features (Learner, Repair, Corrector, Evaluator) will fail.")
    
    orchestrator = OrchestratorAgent()
    orchestrator.initialize()
    
    # Start the scheduler loop
    # orchestrator.start_schedule() 
    
    # For this demonstration/verification, we just run one cycle
    orchestrator.run_cycle()

if __name__ == "__main__":
    main()
