from sqlalchemy.orm import Session
from app.db.models import Job, Certificate, JobStatus, CertStatus
from .certificate_builder import generate_certificate_pdf

def process_job_background(job_id: int, session_factory):
    """Processes a certificate generation job."""
    db: Session = session_factory()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return
            
        job.status = JobStatus.PROCESSING
        db.commit()
        
        certificates = db.query(Certificate).filter(Certificate.job_id == job_id).all()
        
        for cert in certificates:
            try:
                filename = f"cert_{job.id}_{cert.id}.pdf"
                filepath = generate_certificate_pdf(cert.recipient_name, filename)
                
                cert.status = CertStatus.GENERATED
                cert.file_path = filepath
            except Exception as e:
                cert.status = CertStatus.FAILED
                cert.error_message = str(e)
            
            db.commit()
        
        job.status = JobStatus.COMPLETED
        db.commit()
    finally:
        db.close()
