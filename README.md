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


# Bugs Found and Fixing Approach

This document systematically catalogs the bugs encountered in the repository and details the approach used to fix each one. It is intended as a supplement to the main README, providing technical transparency and serving as a debugging reference for future maintainers.

---

## 1. Incorrect Installation Command in README

- **Bug:**  
  The original README listed `pip install -r requirement.txt` instead of the correct `requirements.txt`.
- **Fixing Approach:**  
  Corrected every instance to `pip install -r requirements.txt` and clarified installation steps.

---

## 2. Missing and Mismatched Dependencies

- **Bug:**  
  The original `requirements.txt`:
  - Omitted crucial dependencies like `python-dotenv`, `pypdf`, and `uvicorn`.
  - Included heavy, rarely-used Google libraries with strict versions, causing potential conflicts.
  - Sometimes included libraries not imported or required.
- **Fixing Approach:**  
  - Added missing dependencies with pinned, compatible versions.
  - Added clarifying comments about which dependencies are core and which are optional.
  - Ensured all runtime imports are covered by `requirements.txt`.
  - Added notes for macOS/Apple Silicon compatibility (e.g., `onnxruntime-silicon`).

---

## 3. Python Version Incompatibility

- **Bug:**  
  CrewAI and related packages require Python >=3.10,<3.14, but installs sometimes failed due to Python 3.9 or 3.14+.
- **Fixing Approach:**  
  - Updated documentation to instruct usage of Python 3.11 or 3.12.
  - Provided step-by-step setup for Homebrew, pyenv, and Conda environments.
  - Added compatibility checks before install.

---

## 4. LLM Initialization and Agent Misconfiguration

- **Bug:**  
  - `llm = llm` undefined in `agents.py`.
  - LLM not explicitly initialized with model and API key.
  - Agents used unsafe, hallucination-prone prompts and incorrect `tools` parameter (`tool` instead of `tools` list).
- **Fixing Approach:**  
  - Properly imported and initialized CrewAI LLM with environment variables.
  - Set agent prompts to be professional, factual, and document-grounded.
  - Used `tools=[...]` correctly for CrewAI agents.

---

## 5. PDF Reader Tool Design Flaws

- **Bug:**  
  - Used an undefined class or imported `Pdf`.
  - The reader was not compatible as a CrewAI tool.
  - Lacked robust error handling and whitespace normalization.
- **Fixing Approach:**  
  - Rebuilt the PDF tool using `pypdf` for reliable extraction.
  - Decorated tool with `@tool`.
  - Implemented whitespace normalization and explicit error raising for missing files or unreadable content.

---

## 6. Hallucination-Prone and Unsafe Task Prompts

- **Bug:**  
  - Tasks encouraged making up data or providing fake links.
  - No clear instruction to ground answers only in the provided document.
- **Fixing Approach:**  
  - Rewrote all prompts to be fact-based, conservative, and safe.
  - Added explicit instructions to only use document data and note uncertainties.

---

## 7. Main Application (main.py) Logic Issues

- **Bug:**  
  - Name collisions between route functions and imported tasks.
  - File handling logic did not align with tool expectations (wrong PDF path).
  - No result persistence; results lost after restart.
  - Minimal input validation.
- **Fixing Approach:**  
  - Aliased task imports to avoid naming conflicts.
  - Ensured uploaded PDF is always saved to the path used by the tool.
  - Added SQLite database for persistent result storage.
  - Added robust input validation and error handling.
  - Provided endpoints to fetch past analyses.

---

## 8. Bonus: Queue/Worker Scalability (Design Pattern, not implemented)

- **Bug/Limit:**  
  - The original code was synchronous; for scale, an async/queue-based approach is preferable.
- **Fixing Approach:**  
  - Documented how to implement with Redis + RQ/Celery.
  - Suggested API pattern for background job submission and polling.

---

## 9. General Code Hygiene

- **Bug:**  
  - Inconsistent variable naming, missing docstrings, unused imports.
  - No clear separation between core logic and optional expansion.
- **Fixing Approach:**  
  - Cleaned up variable naming for clarity.
  - Added docstrings and comments.
  - Moved expansion hooks to optional classes/sections.

---

## 10. Environment Variable Handling

- **Bug:**  
  - `.env` not always loaded before use, leading to missing API keys at runtime.
- **Fixing Approach:**  
  - Ensured `dotenv` is loaded at the top of each relevant file.
  - Clarified `.env` setup in documentation.

---

## Conclusion

By addressing these issues, the repository is now:
- Stable and reliable to install and run
- Safer and more professional in its LLM prompting
- Robust in its PDF handling and result persistence
- Easier to maintain and extend

If further bugs are discovered, please update this document with a new section per bug.

