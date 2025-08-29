# Financial Document Analyzer

A FastAPI + CrewAI service that analyzes financial PDF documents using a properly configured agent and a robust PDF reader tool. This repo contains a cleaned, working codebase with professional, safety-compliant agents and tasks.

## Contents
- Fully working FastAPI service
- CrewAI agent with a proper LLM configuration
- PDF reading tool using pypdf
- SQLite storage for analysis results (bonus)
- API endpoints with /docs (Swagger UI)
- Detailed bugs & fixes log

## Prerequisites
- Python 3.10+
- An OpenAI API key (for default LLM)
- Optional: SERPER_API_KEY if you choose to use search (not required for core flow)

## Installation
```sh
git clone https://github.com/shiveshmishra46/ai-project.git
cd ai-project
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a .env file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
# SERPER_API_KEY=your_serper_key_if_you_plan_to_use_search
```

## Running
```sh
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Open http://localhost:8000/docs to test endpoints.

## Usage
1) POST /analyze
   - Upload a PDF file and optional query string.
   - The PDF is saved to data/sample.pdf (used by the reader tool) and also to a unique file for record.
   - The Crew runs a grounded analysis on the document and stores the result in SQLite (data/results.db).
   - Response includes the analysis and an inserted analysis_id.

2) GET /analyses
   - List recent analyses (id, filename, query, created_at).

3) GET /analyses/{id}
   - Fetch a single analysis result by ID.

## API Documentation (Quick)
- GET /: Health check
- POST /analyze: multipart/form-data
  - file: UploadFile (required)
  - query: str (optional; defaults to: “Analyze this financial document for investment insights”)
- GET /analyses
- GET /analyses/{id}

## Data & Storage
- Uploaded file is written to:
  - data/sample.pdf (used by the tool)
  - data/financial_document_{uuid}.pdf (temporary copy cleaned up after run)
- Results stored in data/results.db (SQLite):
  - id (TEXT, primary key)
  - filename (TEXT)
  - query (TEXT)
  - analysis (TEXT)
  - created_at (TEXT)

## Bugs Found & Fixes

1) requirements.txt
- Bug: Missing python-dotenv and pypdf; missing uvicorn for server.
- Fix: Added python-dotenv, pypdf, uvicorn[standard].

2) README.md
- Bug: Incorrect installation command (requirement.txt instead of requirements.txt).
- Fix: Corrected and added complete setup, usage, and API docs.

3) agents.py
- Bug: llm = llm undefined; unsafe prompts; incorrect tools parameter (tool vs tools).
- Fix: Proper LLM initialization (CrewAI LLM with OPENAI_API_KEY/OPENAI_MODEL). Safe, professional agent content. Used tools=[...].

4) tools.py
- Bug: Pdf loader undefined; async tool not compatible with CrewAI tools; no decorator.
- Fix: Implemented robust PDF reader with pypdf and decorated with @tool so CrewAI can use it. Kept the interface name read_data_tool.

5) task.py
- Bug: Hallucination-prone instructions; fake URLs encouraged; tools previously not usable.
- Fix: Professional, document-grounded instructions. Kept analyze_financial_document as the primary task with the working PDF tool.

6) main.py
- Bug: Name collision between route function and imported task; run_crew ignores file path; tool expects data/sample.pdf; lack of persistence.
- Fix: Aliased task import; ensure uploaded PDF is saved to data/sample.pdf; added SQLite persistence; added endpoints to retrieve results.

## Bonus Points

- Queue/Worker Model:
  - Recommended approach: Add Redis + RQ/Celery to offload the Crew run. Pattern:
    - POST /analyze enqueues job -> worker processes -> store result -> client polls GET /analyses/{id}.
  - This repo currently runs synchronously for simplicity and reliability.

- Database Integration:
  - Implemented a minimal SQLite persistence layer (std lib sqlite3) to store analyses.

## Notes
- By default the agent uses OpenAI (gpt-4o-mini) via CrewAI’s LLM wrapper. You can swap OPENAI_MODEL in .env.
- The service is designed to be factual and document-grounded. If data is missing, it will say so rather than hallucinate.
