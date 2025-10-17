"""
MOCK Azure AD OAuth2 token manager for local development.
This simulates the real Azure AD authentication without requiring actual credentials.

To use REAL Azure AD, switch USE_MOCK_AZURE_AD=false in .env and ensure real credentials are set.
"""
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MockAzureADTokenManager:
    """
    Mock Azure AD token manager that simulates token acquisition.

    This is used for local development when you don't have access to
    the actual Azure AD tenant or AskAT&T/AskDocs endpoints.
    """

    def __init__(self):
        """Initialize mock token manager."""
        self._mock_token = "mock_azure_ad_token_12345"
        self._token_expiry = datetime.utcnow() + timedelta(hours=1)
        logger.info("MOCK Azure AD Token Manager initialized (for local development)")

    def get_access_token(self) -> Optional[str]:
        """
        Get a mock access token.

        In production, this would:
        1. Check if cached token is still valid
        2. Request new token from Azure AD if needed
        3. Return access token

        For development, we just return a mock token.

        Returns:
            Mock access token string
        """
        # Simulate token refresh if expired
        if datetime.utcnow() >= self._token_expiry:
            logger.info("Mock token expired, generating new mock token")
            self._mock_token = f"mock_azure_ad_token_{datetime.utcnow().timestamp()}"
            self._token_expiry = datetime.utcnow() + timedelta(hours=1)

        logger.debug(f"Returning mock Azure AD token: {self._mock_token[:20]}...")
        return self._mock_token


# Global singleton instance
token_manager = MockAzureADTokenManager()
