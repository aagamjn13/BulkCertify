# BulkCertify - Bulk Certificate Generator

BulkCertify is a complete full-stack web application designed to generate professional PDF certificates in bulk using a beautiful, dynamic frontend and a robust asynchronous backend.

## 🚀 Tech Stack

### Frontend
- **Structure:** Vanilla HTML5
- **Styling:** Vanilla CSS3 (Custom properties, Glassmorphism, CSS Animations, Dark Mode Aesthetic)
- **Logic:** Vanilla JavaScript (ES6, async/await, Fetch API)

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite with SQLAlchemy ORM
- **PDF Generation:** ReportLab (Vectorized PDF generation)
- **Validation:** Pydantic
- **Asynchronous Tasks:** FastAPI BackgroundTasks

## 🏗️ Architecture

The application is split into a decoupled frontend and backend architecture:

1. **Client (Browser):** A static HTML/CSS/JS frontend that allows users to input recipient details (Name and Email). It communicates with the backend via REST APIs.
2. **REST API (FastAPI):** Exposes endpoints to create certificate generation jobs, poll for status, and download the finished PDFs.
3. **Background Worker:** When a job is submitted, the API immediately responds with an HTTP 202 Accepted. The heavy lifting (generating PDFs via ReportLab) is handed off to a background task so the main thread remains unblocked and responsive.
4. **Database (SQLite):** Tracks the status of each job (`pending`, `processing`, `completed`) and individual certificates to ensure data persistence and allow the frontend to poll for real-time progress.

## 🛠️ How to Run This Project Locally

### 1. Backend Setup

1. **Open a terminal** and navigate to the project directory:
   ```bash
   cd BulkCertify
   ```
2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```
   *The backend API will now be running at `http://127.0.0.1:8000`.*

### 2. Frontend Setup

Since the frontend consists of plain HTML/CSS/JS files, you simply need to serve them. We recommend using Python's built-in HTTP server to avoid caching and auto-reload issues.

1. **Open a SECOND terminal** in the same project directory.
2. **Start a local static server** pointing to the frontend folder:
   ```bash
   python -m http.server 5500 --directory frontend
   ```
3. **Open your web browser** and go to:
   [http://localhost:5500](http://localhost:5500)

You can now add recipients, hit "Generate Certificates," and watch the background worker process them in real-time!

## 🧪 Running Tests

Tests are written using `pytest`. They cover API endpoint behavior, job creation, background processing, and error handling.

```bash
pytest
```

## ⚙️ REST API Endpoints

If you prefer to interact with the API directly (or via Swagger UI at `http://127.0.0.1:8000/docs`), here are the core endpoints:

- **`POST /jobs/`**: Submit a bulk request by passing a list of recipients. Returns a Job ID.
- **`GET /jobs/{job_id}`**: Returns the real-time status of the job and each individual certificate.
- **`GET /certificates/{cert_id}/download`**: Downloads the generated PDF file.

## 🛡️ Fault Tolerance

The backend generation loop handles exceptions gracefully. If a single certificate fails to generate (e.g., due to a bad character or file system error), the system records the error for that specific certificate and continues processing the rest of the batch without crashing the entire job.
