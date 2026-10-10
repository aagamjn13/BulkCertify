import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import time
import os
import shutil

from app.main import app
from app.db.database import Base
from app.api.dependencies import get_db
from app.core.config import settings
from app.db.models import JobStatus, CertStatus

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Patch the background task session factory
import app.api.routes.jobs as jobs_routes
jobs_routes.SessionLocal = TestingSessionLocal

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Ensure a clean directory for certs
    if os.path.exists(settings.CERTIFICATES_DIR):
        shutil.rmtree(settings.CERTIFICATES_DIR)
    os.makedirs(settings.CERTIFICATES_DIR)
    
    yield
    Base.metadata.drop_all(bind=engine)
    # Cleanup after test
    if os.path.exists(settings.CERTIFICATES_DIR):
        shutil.rmtree(settings.CERTIFICATES_DIR)

client = TestClient(app)

def test_create_job():
    response = client.post(
        "/jobs/",
        json={
            "recipients": [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"}
            ]
        },
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["certificates"]) == 2
    assert data["certificates"][0]["recipient_name"] == "Alice"

def test_create_job_empty_recipients():
    response = client.post("/jobs/", json={"recipients": []})
    assert response.status_code == 400

def test_job_processing_and_status():
    response = client.post(
        "/jobs/",
        json={
            "recipients": [
                {"name": "Charlie", "email": "charlie@example.com"}
            ]
        },
    )
    job_id = response.json()["id"]
    
    # Wait for the background task to finish
    time.sleep(1)
    
    response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["certificates"][0]["status"] == "generated"
    assert data["certificates"][0]["file_path"] is not None

def test_individual_certificate_failure():
    # 'fail_me' is hardcoded to fail in services/certificate_builder.py
    response = client.post(
        "/jobs/",
        json={
            "recipients": [
                {"name": "Valid User", "email": "valid@example.com"},
                {"name": "fail_me", "email": "fail@example.com"}
            ]
        },
    )
    job_id = response.json()["id"]
    
    time.sleep(1)
    
    response = client.get(f"/jobs/{job_id}")
    data = response.json()
    assert data["status"] == "completed"
    
    certs = data["certificates"]
    assert len(certs) == 2
    
    valid_cert = next(c for c in certs if c["recipient_name"] == "Valid User")
    failed_cert = next(c for c in certs if c["recipient_name"] == "fail_me")
    
    assert valid_cert["status"] == "generated"
    assert failed_cert["status"] == "failed"
    assert failed_cert["error_message"] is not None

def test_download_certificate():
    response = client.post(
        "/jobs/",
        json={
            "recipients": [
                {"name": "Download User", "email": "dl@example.com"}
            ]
        },
    )
    job_id = response.json()["id"]
    
    time.sleep(1)
    
    job_response = client.get(f"/jobs/{job_id}")
    cert_id = job_response.json()["certificates"][0]["id"]
    
    dl_response = client.get(f"/certificates/{cert_id}/download")
    assert dl_response.status_code == 200
    assert dl_response.headers["content-type"] == "application/pdf"
