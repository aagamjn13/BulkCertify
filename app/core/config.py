from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bulk Certificate Generator"
    DATABASE_URL: str = "sqlite:///./bulkcertify.db"
    CERTIFICATES_DIR: str = "generated_certificates"

    class Config:
        env_file = ".env"

settings = Settings()

if not os.path.exists(settings.CERTIFICATES_DIR):
    os.makedirs(settings.CERTIFICATES_DIR)
