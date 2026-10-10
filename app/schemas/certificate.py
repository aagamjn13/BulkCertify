from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.db.models import CertStatus

class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    recipient_email: str
    status: CertStatus
    error_message: Optional[str] = None
    file_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
