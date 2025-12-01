#AI Agentic Job Hunter: Autonomous Career Assistant#
Subtitle
A Multi-Agent System that Scrapes, Validates, and Ranks Job Opportunities using Your Unique "Success Persona"

###Project Description###
Overview
Finding the perfect job is a time-consuming process involving searching multiple platforms, filtering through irrelevant listings, and assessing cultural fit. AI Agentic Job Hunter automates this entire pipeline. It is an intelligent, multi-agent system designed to act as your personal 24/7 career recruiter.
Unlike simple scrapers that just match keywords, this system builds a deep understanding of the user's career profile (the "Success Persona") by analyzing their CV and interview notes. It then autonomously scouts the web, filters out noise, and ranks opportunities based on how well they align with the user's skills, experience, and career goals.

###Key Features###
•	Multi-Source Scraping: Simultaneously scrapes major job boards including LinkedIn, Indeed, TotalJobs, Reed, CWJobs, and Glassdoor.
•	Intelligent Parsing: Uses Large Language Models (LLM) to extract structured data (salary, location, job type) from unstructured HTML, handling complex layouts that break traditional regex scrapers.
•	Persona-Based Scoring: The Learner Agent analyzes your CV and interview history to create a "Success Persona". The Evaluator Agent then uses this persona to score every job from 0-100, ensuring you only see the most relevant opportunities.
•	Autonomous Validation: The Validator Agent filters out spam, stale listings (older than 7 days), and jobs outside your target industries before they even reach your dashboard.
•	Self-Healing Architecture: The Self-Corrector Agent monitors the system for critical errors. If a scraper breaks due to a site layout change, it can analyze the error log and the source code, propose a fix using an LLM, and apply it automatically (with human approval).
•	Interactive Dashboard: A modern React-based UI allows users to configure search parameters, view live logs, and manage their job pipeline.

###System Architecture###
The application is built as a modular, event-driven system:
•	Frontend: React + Vite + TailwindCSS for a responsive, high-performance user interface.
•	Backend: FastAPI (Python) serving REST endpoints and managing background tasks.
•	Database: SQLite with SQLAlchemy ORM for persistent storage of jobs, logs, and configuration.
•	Scraping Engine: Playwright (Python) for robust, browser-based scraping that handles dynamic JavaScript content.
•	AI Core: Google Gemini 2.0 Flash for high-speed, cost-effective reasoning, parsing, and code generation.

###Multi-Agent Architecture###
The system employs a team of specialized agents working in concert:
1.	Orchestrator Agent: The project manager. It schedules runs, manages the workflow pipeline (Scrape -> Validate -> Deduplicate -> Score -> Save), and handles inter-agent communication.
2.	Learner Agent: The analyst. It reads the user's CV and interview notes to construct and continuously refine the "Success Persona" JSON file, which serves as the ground truth for what a "good job" looks like.
3.	Worker (Scraper): The scout. It executes Playwright scripts to fetch raw job data from configured sources. It handles pagination, anti-bot detection (basic), and HTML parsing.
4.	Validator Agent: The gatekeeper. It performs data integrity checks (missing fields), enforces business rules (e.g., "posted within 7 days"), and uses an LLM to verify industry relevance.
5.	Evaluator Agent: The recruiter. It takes validated jobs and uses the LLM to compare them against the "Success Persona", assigning a match score (0-100) and providing a reasoning summary for why the job is a good fit.
6.	Self-Corrector Agent: The engineer. It watches for repeated critical errors. If detected, it reads the error logs and the failing code, prompts the LLM to generate a patch, and can apply the fix to "heal" the system at runtime.

###Data Flow###
1.	Initialization: User uploads CV/Notes. Learner builds Persona. User configures keywords/sources via UI.
2.	Trigger: Orchestrator wakes up (on schedule or manual trigger).
3.	Acquisition: Scraper visits enabled sites, extracts raw job cards, and fetches detailed descriptions.
4.	Validation: Raw jobs are passed to Validator. Invalid or irrelevant jobs are discarded.
5.	Deduplication: Orchestrator checks against the DB and the current batch to remove duplicates.
6.	Evaluation: Unique, valid jobs are sent to Evaluator. Each job gets a match_score and match_reasoning.
7.	Persistence: Scored jobs are saved to SQLite.
8.	Presentation: User views ranked jobs in the Dashboard, provides feedback (which feeds back into the Learner for future cycles).

###Code Structure###
•	agents/: Contains the logic for all agents (Orchestrator, Learner, Validator, Evaluator, Corrector).
•	backend/: FastAPI application, database models, and API routes.
•	frontend/: React application source code.
•	job_scraper.py: Core Playwright scraping logic.
•	utils/: Helper functions for LLM interaction and persistence.
•	CV/ & Job Interview/: Directories for user context files.
