from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.db.database import Base, engine
from app.core.config import settings
from app.api.router import api_router

# Create DB tables (In a real professional project, Alembic would be used instead)
Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A backend API to generate certificates in bulk.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

app.include_router(api_router)
