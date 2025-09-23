from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    # Database Configuration
    # For production (Google Cloud Run), use Supabase Postgres
    # For local development, use SQLite
    DATABASE_URL: str = "sqlite:///./malabro_eshop.db"
    
    # Supabase Postgres URL (for production)
    SUPABASE_DB_URL: str = ""

    # Environment detection
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Configuration
    API_V1_STR: str = "/api/v1"

    # Supabase Configuration
    SUPABASE_URL: str = Field(default="", env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(default="", env="SUPABASE_KEY")
    SUPABASE_ANON_KEY: str = ""

    # JWT Configuration
    SECRET_KEY: str = Field(default="p2qn3phhWtwPlTUXWOavE9adm9g/GfxYlwWlIY/nWTY5XAcCCFYSTspvmA3zXbJzsxrDaHWSY3ahfNt0EI+2mA==", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 8 days

    # First Superuser
    FIRST_SUPERUSER: str = "admin@malabro.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8080"])
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175"
    
    # Email Configuration (SMTP)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SENDGRID_FROM_EMAIL: str = ""
    ADMIN_EMAIL: str = "admin@malabro.com"
    
    # Groq AI Configuration
    GROQ_API_KEY: str = Field(default="", env="GROQ_API_KEY")

    @property
    def database_url(self) -> str:
        """Get the appropriate database URL based on environment"""
        if self.ENVIRONMENT == "production" and self.SUPABASE_DB_URL:
            return self.SUPABASE_DB_URL
        return self.DATABASE_URL

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
