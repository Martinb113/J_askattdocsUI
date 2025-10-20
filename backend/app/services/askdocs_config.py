"""
Service for fetching AskDocs configurations from external API.
Uses Azure AD OAuth2 authentication (same as AskAT&T and AskDocs).
"""
import httpx
import logging
from typing import Optional
from app.config import settings
from app.services.azure_ad import get_askatt_token

logger = logging.getLogger(__name__)


async def fetch_configurations_by_domain(
    domain_name: str,
    log_as_userid: str,
    environment: str = "production"
) -> str:
    """
    Fetch configurations for a specific domain from external AskDocs API.

    Uses Azure AD OAuth2 authentication with domain scope (same as AskDocs).

    Args:
        domain_name: The domain identifier to fetch configurations for
        log_as_userid: User ID for logging purposes
        environment: "stage" or "production" (default: "production")

    Returns:
        String response from the API containing configuration data

    Raises:
        HTTPError: If the API request fails
        TimeoutException: If the request times out
    """
    # Get Azure AD access token (domain scope, same as AskDocs)
    try:
        access_token = await get_askatt_token(use_domain_scope=True)
        logger.info(f"Successfully obtained Azure AD token for configuration fetch")
    except Exception as e:
        logger.error(f"Failed to get Azure AD token: {str(e)}")
        raise Exception(f"Authentication failed: {str(e)}")

    # Select the appropriate API base URL
    if environment == "stage":
        base_url = settings.ASKDOCS_CONFIG_API_STAGE
    else:
        base_url = settings.ASKDOCS_CONFIG_API_PRODUCTION

    # Construct full endpoint URL
    url = f"{base_url}/admin/v2/list-config-by-domain"

    # Prepare request payload
    payload = {
        "domain": domain_name,
        "log_as_userid": log_as_userid
    }

    # Prepare headers with Azure AD token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    logger.info(f"Fetching configurations for domain: {domain_name} from {url}")
    logger.debug(f"Payload: {payload}")

    # Make HTTP POST request with authentication
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for 4xx/5xx responses

        logger.info(f"Successfully fetched configurations for domain: {domain_name}")
        logger.debug(f"Response: {response.text[:200]}...")  # Log first 200 chars

        # Return response as string (as per API specification)
        return response.text


async def fetch_configurations_by_domain_mock(
    domain_name: str,
    log_as_userid: str,
    environment: str = "production"
) -> str:
    """
    Mock implementation for local development.

    Args:
        domain_name: The domain identifier
        log_as_userid: User ID for logging
        environment: "stage" or "production"

    Returns:
        Mock JSON string with sample configurations
    """
    import json
    from datetime import datetime

    # Define realistic mock configurations per domain
    mock_domain_configs = {
        "SD_International": [
            {
                "config_key": "sim_wiki_con_v1v1",
                "display_name": "SIM Wiki Configuration v1.1",
                "description": "Service Information Management wiki configuration for international teams",
                "version": "1.1",
                "is_active": True,
                "created_at": "2024-01-15T10:00:00Z",
                "metadata": {
                    "team": "SD International",
                    "content_type": "wiki",
                    "region": "global"
                }
            },
            {
                "config_key": "ois_wiki_com_v1v1",
                "display_name": "OIS Wiki Configuration v1.1",
                "description": "Operational Information System wiki configuration for SD International",
                "version": "1.1",
                "is_active": True,
                "created_at": "2024-02-20T14:30:00Z",
                "metadata": {
                    "team": "SD International",
                    "content_type": "wiki",
                    "region": "global"
                }
            }
        ],
        "att_support": [
            {
                "config_key": "att_support_kb_v1",
                "display_name": "AT&T Support Knowledge Base v1",
                "description": "Primary knowledge base for AT&T customer support",
                "version": "1.0",
                "is_active": True,
                "created_at": "2023-11-10T09:00:00Z",
                "metadata": {
                    "team": "Customer Support",
                    "content_type": "knowledge_base",
                    "region": "US"
                }
            },
            {
                "config_key": "att_support_faq_v2",
                "display_name": "AT&T Support FAQ v2",
                "description": "Frequently asked questions for AT&T services",
                "version": "2.0",
                "is_active": True,
                "created_at": "2024-03-05T11:15:00Z",
                "metadata": {
                    "team": "Customer Support",
                    "content_type": "faq",
                    "region": "US"
                }
            }
        ]
    }

    # Get configurations for the requested domain, or generate generic ones
    if domain_name in mock_domain_configs:
        configurations = mock_domain_configs[domain_name]
    else:
        # Generic fallback for unknown domains
        configurations = [
            {
                "config_key": f"{domain_name}_v1",
                "display_name": f"{domain_name.replace('_', ' ').title()} V1",
                "description": f"Version 1 configuration for {domain_name}",
                "version": "1.0",
                "is_active": True,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "metadata": {
                    "team": "General",
                    "content_type": "generic"
                }
            }
        ]

    # Mock response data
    mock_configs = {
        "domain": domain_name,
        "environment": environment,
        "configurations": configurations,
        "total_count": len(configurations),
        "logged_as": log_as_userid,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    return json.dumps(mock_configs, indent=2)
