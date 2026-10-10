from fastapi import FastAPI
from app.db.database import Base, engine
from app.core.config import settings
from app.api.router import api_router

# Create DB tables (In a real professional project, Alembic would be used instead)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A backend API to generate certificates in bulk.",
    version="1.0.0"
)

app.include_router(api_router)
