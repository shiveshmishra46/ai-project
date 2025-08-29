# API Documentation

This document describes the endpoints, request/response formats, and usage examples for the Financial Document Analyzer API.

---

## Base URL

```
http://localhost:8000/
```

---

## Endpoints

### 1. Health Check

**GET /**

Returns a simple status message to verify the API is running.

**Response**
```json
{
  "message": "Financial Document Analyzer API is running"
}
```

---

### 2. Analyze Financial Document

**POST /analyze**

Uploads a financial PDF and receives an AI-generated analysis.

**Request (multipart/form-data)**
- **file** (required): The PDF file to analyze.  
- **query** (optional): A custom analysis prompt. Defaults to "Analyze this financial document for investment insights".

**Example using `curl`:**
```sh
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@/path/to/your/financial.pdf" \
  -F "query=Summarize the key financial highlights."
```

**Response**
```json
{
  "status": "success",
  "analysis_id": "e9a7c7d6-4f1c-4f66-9c68-7e8fdc8b7fbb",
  "query": "Summarize the key financial highlights.",
  "analysis": "<AI-generated summary and highlights here>",
  "file_processed": "financial.pdf"
}
```

---

### 3. List Recent Analyses

**GET /analyses?limit=20**

Returns metadata for the most recent analyses.

**Parameters**
- **limit** (optional): Number of results to return (default: 20).

**Response**
```json
{
  "results": [
    {
      "id": "e9a7c7d6-4f1c-4f66-9c68-7e8fdc8b7fbb",
      "filename": "financial.pdf",
      "query": "Summarize the key financial highlights.",
      "created_at": "2025-08-29T13:00:00.000000"
    },
    ...
  ]
}
```

---

### 4. Get Analysis by ID

**GET /analyses/{analysis_id}**

Retrieves the full analysis for a specific upload.

**Path Parameter**
- **analysis_id**: The unique ID returned from `/analyze`.

**Response**
```json
{
  "id": "e9a7c7d6-4f1c-4f66-9c68-7e8fdc8b7fbb",
  "filename": "financial.pdf",
  "query": "Summarize the key financial highlights.",
  "analysis": "<AI-generated summary and highlights here>",
  "created_at": "2025-08-29T13:00:00.000000"
}
```

---

## Notes

- OpenAPI/Swagger documentation is available at `/docs` when the app is running.
- All endpoints return JSON.
- Analyses are persisted in a local SQLite database.
- Uploaded files are temporarily stored and cleaned up after processing (except for a canonical copy used for analysis).

---

## Error Responses

- 404 Not Found: Analysis ID does not exist.
- 500 Internal Server Error: Processing error, missing file, or invalid PDF.
- All errors return a JSON payload describing the issue.

---

## Example Workflow

1. **Upload and analyze a PDF:**  
   Send a `POST /analyze` with your PDF file.
2. **Get analysis ID from response.**
3. **Retrieve analysis later:**  
   Use `GET /analyses/{analysis_id}` to fetch the full result.
4. **List past analyses:**  
   Use `GET /analyses` to see all recent uploads and their queries.

---

For further questions, see the main README, or contact the repository maintainer.
