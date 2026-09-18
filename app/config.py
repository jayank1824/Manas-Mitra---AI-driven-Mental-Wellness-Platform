import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = "Manas Mitra"
    APP_DESCRIPTION: str = "AI-Powered Mental Wellness Platform"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "manas-mitra-dev-secret-key-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/manas_mitra.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    UPLOAD_DIR: str = "app/static/uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024

    def __init__(self):
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)

settings = Settings()

