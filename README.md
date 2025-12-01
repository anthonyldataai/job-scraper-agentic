🚀 AI Agentic Job Hunter
Autonomous Career Assistant — A Multi-Agent System for Scraping, Validating & Ranking Jobs Using Your Unique Success Persona

Your 24/7 autonomous AI recruiter that analyzes your CV, learns your persona, scouts multiple job boards, filters noise, validates listings, and ranks opportunities by true personal fit.

🌟 Key Features

🔍 Multi-Source Scraping
Scrapes LinkedIn, Indeed, TotalJobs, Reed, CWJobs, Glassdoor — all in parallel.

🧠 LLM-Powered Parsing
Extracts structured data from messy HTML using advanced reasoning (not regex).

🧩 Persona-Based Scoring
Learner Agent creates a “Success Persona” from your CV & interview notes.
Evaluator Agent scores every job 0–100 based on actual personal fit.

🔒 Autonomous Validation
Filters spam, stale jobs (>7 days), irrelevant industries — before they reach you.

🔧 Self-Healing Architecture
If a scraper breaks, the Self-Corrector Agent analyzes logs, proposes LLM-generated patches, and applies fixes (with your approval).

📊 Interactive Dashboard
React UI with live logs, configuration controls, and a personalized job pipeline.

📝 Project Description

Finding the ideal job requires navigating multiple platforms, evaluating relevance, and determining cultural alignment — a tedious, manual process.

AI Agentic Job Hunter automates the entire pipeline.
It goes far beyond keyword matching by building a deep understanding of your skills, history, and goals. It continuously scouts the web, filters irrelevant roles, and ranks jobs based on how well they match your evolving Success Persona.

🧱 System Architecture
flowchart LR
    A[Frontend<br>React + Vite + Tailwind] --> C[FastAPI Backend]
    B[Playwright Scrapers] --> C
    C --> D[SQLite + SQLAlchemy]
    C --> E[Google Gemini 2.0 Flash<br>AI Core]

Tech Stack:

🎨 Frontend: React, Vite, TailwindCSS

⚙️ Backend: FastAPI + Background Tasks

🗄️ Database: SQLite + SQLAlchemy ORM

🌐 Scraper Engine: Playwright (Python)

🤖 AI Engine: Google Gemini 2.0 Flash

🤖 Multi-Agent Architecture
| Agent                    | Role                                                                                  |
| ------------------------ | ------------------------------------------------------------------------------------- |
| **Orchestrator Agent**   | Schedules runs and manages pipeline: *Scrape → Validate → Deduplicate → Score → Save* |
| **Learner Agent**        | Builds & updates the *Success Persona* from CV + interview notes                      |
| **Worker (Scraper)**     | Fetches job listings, handles pagination, anti-bot behavior, HTML parsing             |
| **Validator Agent**      | Enforces rules (freshness, completeness, industry relevance)                          |
| **Evaluator Agent**      | Ranks jobs 0–100 based on persona match + explains reasoning                          |
| **Self-Corrector Agent** | Detects recurring failures, generates patches, and applies fixes                      |

🔄 Data Flow
sequenceDiagram
    participant U as User
    participant L as Learner Agent
    participant S as Scraper
    participant V as Validator
    participant E as Evaluator
    participant DB as SQLite

    U->>L: Upload CV + Notes
    L->>U: Build Success Persona

    U->>S: Start scheduled run
    S->>V: Raw job data
    V->>E: Validated jobs
    E->>DB: Scored jobs (0–100)
    U->>DB: View ranked jobs in dashboard
Pipeline Summary:

Initialization: CV → Success Persona

Trigger: Manual or scheduled run

Acquisition: Scraper gathers job listings

Validation: Spam, staleness, relevance checks

Deduplication

Evaluation: Persona-based scoring

Persistence: Jobs stored in SQLite

Presentation: Dashboard ranking & feedback loop

📁 Code Structure
📦 AI-Agentic-Job-Hunter
├── agents/
│   ├── orchestrator.py
│   ├── learner.py
│   ├── validator.py
│   ├── evaluator.py
│   └── self_corrector.py
├── backend/
│   ├── api/
│   ├── models/
│   └── main.py
├── frontend/
│   └── src/
├── job_scraper.py
├── utils/
│   ├── llm.py
│   └── persistence.py
├── CV/
└── Job Interview/
