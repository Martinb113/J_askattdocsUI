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
    # SECURITY: These values MUST come from .env file - never hardcode secrets!
    # Get these from Azure Portal: https://portal.azure.com
    AZURE_TENANT_ID: str
    AZURE_CLIENT_ID: str
    AZURE_CLIENT_SECRET: str
    AZURE_SECRET_ID: str

    # Azure AD OAuth2 URLs and Scopes
    # These are constructed from tenant/client IDs in .env file
    AZURE_AUTH_URL: str
    AZURE_SCOPE_ASKATT_GENERAL: str
    # Note: Client credential flows require /.default suffix (per Azure AD error AADSTS1002012)
    AZURE_SCOPE_ASKATT_DOMAIN: str

    # AskAT&T API Configuration
    # Internal API URLs - these should come from .env file
    ASKATT_API_BASE_URL_STAGE: str
    ASKATT_API_BASE_URL_PRODUCTION: str
    ASKATT_DOMAIN_NAME: str = "GenerativeAI"
    ASKATT_MODEL_NAME: str = "gpt-4o"
    ASKATT_MAX_TOKENS: int = 800

    # AskDocs API (optional when using MOCK)
    # These URLs should come from .env file to allow different environments
    ASKDOCS_API_BASE_URL_STAGE: str
    ASKDOCS_API_BASE_URL_PRODUCTION: str

    # AskDocs Configuration API Endpoints (for fetching domain configurations)
    ASKDOCS_CONFIG_API_STAGE: str
    ASKDOCS_CONFIG_API_PRODUCTION: str

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:3001"

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
