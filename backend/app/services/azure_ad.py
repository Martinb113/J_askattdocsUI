"""
Azure AD OAuth2 authentication service for AskAT&T API.
"""
import httpx
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AzureADTokenManager:
    """Manages Azure AD OAuth2 tokens for API authentication."""

    def __init__(self):
        self._token: Optional[str] = None
        self._token_type: Optional[str] = None

    async def get_access_token(self, scope: Optional[str] = None) -> str:
        """
        Get an access token from Azure AD using client credentials flow.

        Args:
            scope: OAuth2 scope (defaults to AZURE_SCOPE_ASKATT_GENERAL)

        Returns:
            Access token string

        Raises:
            HTTPError: If token request fails
        """
        # Use provided scope or default to general AskAT&T scope
        token_scope = scope or settings.AZURE_SCOPE_ASKATT_GENERAL

        # Prepare the payload for the token request
        payload = {
            'client_id': settings.AZURE_CLIENT_ID,
            'client_secret': settings.AZURE_CLIENT_SECRET,
            'scope': token_scope,
            'grant_type': 'client_credentials'
        }

        try:
            # Make the request to the authentication server
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    settings.AZURE_AUTH_URL,
                    data=payload,
                    timeout=30.0
                )
                response.raise_for_status()

                token_data = response.json()
                self._token = token_data['access_token']
                self._token_type = token_data.get('token_type', 'Bearer')

                logger.info(f"Successfully obtained Azure AD token with scope: {token_scope}")
                return self._token

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to retrieve Azure AD token: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error during Azure AD authentication: {str(e)}")
            raise

    def get_cached_token(self) -> Optional[str]:
        """
        Get the cached token without making a new request.

        Returns:
            Cached token or None if not available
        """
        return self._token


# Global token manager instance
azure_token_manager = AzureADTokenManager()


async def get_askatt_token(use_domain_scope: bool = False) -> str:
    """
    Get an Azure AD token for AskAT&T API.

    Args:
        use_domain_scope: If True, use domain QnA scope, otherwise use general scope

    Returns:
        Access token string
    """
    scope = settings.AZURE_SCOPE_ASKATT_DOMAIN if use_domain_scope else settings.AZURE_SCOPE_ASKATT_GENERAL
    return await azure_token_manager.get_access_token(scope)
