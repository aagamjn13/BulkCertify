from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List
from datetime import datetime
from app.db.models import JobStatus
from .certificate import CertificateResponse

class RecipientInput(BaseModel):
    name: str
    email: EmailStr

class JobCreateRequest(BaseModel):
    recipients: List[RecipientInput]

class JobResponse(BaseModel):
    id: int
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    certificates: List[CertificateResponse] = []

    model_config = ConfigDict(from_attributes=True)
