from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from .database import Base

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CertStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATED = "generated"
    FAILED = "failed"

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    certificates = relationship("Certificate", back_populates="job", cascade="all, delete-orphan")

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    status = Column(SQLEnum(CertStatus), default=CertStatus.PENDING)
    error_message = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    
    job = relationship("Job", back_populates="certificates")
