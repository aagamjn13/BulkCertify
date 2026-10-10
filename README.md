# Bulk Certificate Generator

A backend API to generate certificates in bulk using a single predefined template.

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite (via SQLAlchemy ORM)
- **PDF Generation**: ReportLab
- **Validation**: Pydantic

## Project Setup

1. **Navigate to the repository folder**:
   ```bash
   cd d:\VSCode\WebD\projects\BulkCertify\BulkCertify
   ```
   
2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Run the server locally using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
API Documentation (Swagger UI) is automatically available at `http://127.0.0.1:8000/docs`.

## Running Tests

Tests are written using `pytest`. They cover API endpoint behavior, job creation, processing, error handling, and retrieval.

```bash
pytest
```

## Usage Instructions

### 1. Submit a Certificate Generation Request

Submit a bulk request by passing a list of recipients.

**Endpoint**: `POST /jobs/`

**Request Body**:
```json
{
  "recipients": [
    {
      "name": "Jane Doe",
      "email": "jane@example.com"
    },
    {
      "name": "John Smith",
      "email": "john@example.com"
    }
  ]
}
```

**Response**: (HTTP 202 Accepted) Returns the newly created Job ID and its current pending status.

### 2. Check the Progress of a Request

**Endpoint**: `GET /jobs/{job_id}`

This endpoint returns the current status of the job (`pending`, `processing`, `completed`) along with the status of each individual certificate (`pending`, `generated`, `failed`).

### 3. Retrieve a Generated Certificate

If a certificate has been successfully generated, you can download the PDF.

**Endpoint**: `GET /certificates/{cert_id}/download`

This returns the PDF file for download. If the certificate failed to generate or is pending, it returns a 400 error.

### 4. Handling Failures

To test the application's fault tolerance, submit a recipient with the name `"fail_me"`. This specific name triggers an intentional error during PDF generation. The system will mark that individual certificate as `failed` (saving the error message), but will successfully generate certificates for all other valid recipients in the same job.

## Design Decisions & Implementation Details

- **Bulk Processing via Background Tasks**: FastAPI's `BackgroundTasks` is used to handle certificate generation asynchronously. This allows the API to return a 202 Accepted status immediately instead of keeping the HTTP connection open while processing hundreds of certificates, which could lead to timeouts.
- **Relational Database (SQLite)**: SQLite is used for simplicity and ease of setup. SQLAlchemy ORM is used so the database can easily be swapped for PostgreSQL in a production environment.
- **Resilience**: The generation loop handles exceptions gracefully. A `try-except` block wraps the generation of each certificate. If one fails, the error is recorded, and the loop continues, ensuring partial success is possible.
- **PDF Generation**: `ReportLab` is used to programmatically generate PDFs rather than image manipulation, producing high-quality vectorized documents suitable for printing.
