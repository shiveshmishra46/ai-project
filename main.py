from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import sqlite3
from datetime import datetime

from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document as analyze_financial_document_task

app = FastAPI(title="Financial Document Analyzer")

DATA_DIR = "data"
SAMPLE_PATH = os.path.join(DATA_DIR, "sample.pdf")
DB_PATH = os.path.join(DATA_DIR, "results.db")


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            filename TEXT,
            query TEXT,
            analysis TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_result(analysis_id: str, filename: str, query: str, analysis: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO analyses (id, filename, query, analysis, created_at) VALUES (?, ?, ?, ?, ?)",
        (analysis_id, filename, query, analysis, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def run_crew(query: str):
    """Run the Crew with the primary task"""
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document_task],
        process=Process.sequential,
    )
    # Pass variables used in the task (query). The tool reads from data/sample.pdf.
    result = financial_crew.kickoff({"query": query})
    return result


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
):
    """Analyze financial document and provide grounded insights"""
    unique_id = str(uuid.uuid4())
    unique_path = os.path.join(DATA_DIR, f"financial_document_{unique_id}.pdf")

    try:
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)

        # Save uploaded file to a unique path
        content = await file.read()
        with open(unique_path, "wb") as f:
            f.write(content)

        # Also save/overwrite the shared sample path used by the tool
        with open(SAMPLE_PATH, "wb") as f:
            f.write(content)

        # Validate query
        if not query or not query.strip():
            query = "Analyze this financial document for investment insights"
        query = query.strip()

        # Run Crew
        response = run_crew(query=query)

        # Persist result
        analysis_id = unique_id
        save_result(
            analysis_id=analysis_id,
            filename=file.filename,
            query=query,
            analysis=str(response),
        )

        return {
            "status": "success",
            "analysis_id": analysis_id,
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}",
        )

    finally:
        # Clean up the unique temp file; keep data/sample.pdf for reproducibility
        if os.path.exists(unique_path):
            try:
                os.remove(unique_path)
            except Exception:
                pass  # Ignore cleanup errors


@app.get("/analyses")
async def list_analyses(limit: int = 20):
    """List recent analyses"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, filename, query, created_at FROM analyses ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    data = [
        {"id": r[0], "filename": r[1], "query": r[2], "created_at": r[3]} for r in rows
    ]
    return {"results": data}


@app.get("/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Fetch a single analysis by ID"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, filename, query, analysis, created_at FROM analyses WHERE id = ?",
        (analysis_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {
        "id": row[0],
        "filename": row[1],
        "query": row[2],
        "analysis": row[3],
        "created_at": row[4],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)