"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # JWT Authentication
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 8

    # MOCK Services (for local development)
    USE_MOCK_ASKATT: bool = True
    USE_MOCK_ASKDOCS: bool = True
    USE_MOCK_AZURE_AD: bool = True

    # Azure AD OAuth2
    AZURE_TENANT_ID: str = "mock-tenant-id"
    AZURE_CLIENT_ID: str = "mock-client-id"
    AZURE_CLIENT_SECRET: str = "mock-client-secret"
    AZURE_SCOPE: str = "https://graph.microsoft.com/.default"

    # AskAT&T API (optional when using MOCK)
    ASKATT_API_BASE_URL_STAGE: str = "https://stage-api.askatt.com"
    ASKATT_API_BASE_URL_PRODUCTION: str = "https://api.askatt.com"

    # AskDocs API (optional when using MOCK)
    ASKDOCS_API_BASE_URL_STAGE: str = "https://stage-api.askdocs.com"
    ASKDOCS_API_BASE_URL_PRODUCTION: str = "https://api.askdocs.com"

    # AskDocs Configuration API Endpoints (for fetching domain configurations)
    ASKDOCS_CONFIG_API_STAGE: str = "https://stage-api.askdocs.com"
    ASKDOCS_CONFIG_API_PRODUCTION: str = "https://api.askdocs.com"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Optional
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
