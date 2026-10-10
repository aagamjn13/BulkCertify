from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.db.models import Certificate, CertStatus
import os

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("/{cert_id}/download")
def download_certificate(cert_id: int, db: Session = Depends(get_db)):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if cert.status != CertStatus.GENERATED or not cert.file_path:
        raise HTTPException(status_code=400, detail="Certificate has not been successfully generated yet")
    
    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on server")
        
    return FileResponse(
        cert.file_path, 
        media_type="application/pdf", 
        filename=os.path.basename(cert.file_path)
    )
