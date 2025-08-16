from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://mathrix:dIVwHZyRuDNLuZQMnbpKJFDK8DzuGvaT@dpg-d2g8qoogjchc73arr4q0-a.oregon-postgres.render.com/mathrix")
    
    # Application
    app_name: str = os.getenv("APP_NAME", "Mathrix API")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "production")
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    allowed_origins: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://mathrix-frontend.onrender.com").split(",")
    
    # Email (optional for now)
    smtp_server: Optional[str] = os.getenv("SMTP_SERVER")
    smtp_port: Optional[int] = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
