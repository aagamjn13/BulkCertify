from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.schemas.job import JobResponse, JobCreateRequest
from app.db.models import Job, Certificate, JobStatus, CertStatus
from app.services.job_worker import process_job_background
from app.db.database import SessionLocal

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse, status_code=202)
def create_job(request: JobCreateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not request.recipients:
        raise HTTPException(status_code=400, detail="Recipients list cannot be empty.")
    
    job = Job(status=JobStatus.PENDING)
    db.add(job)
    db.commit()
    db.refresh(job)
    
    for recipient in request.recipients:
        cert = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status=CertStatus.PENDING
        )
        db.add(cert)
    
    db.commit()
    db.refresh(job)
    
    background_tasks.add_task(process_job_background, job.id, SessionLocal)
    
    return job

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
