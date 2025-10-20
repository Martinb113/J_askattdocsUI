"""
AskDocs API service using real Azure AD authentication and API format.
Provides domain-specific RAG (Retrieval-Augmented Generation) responses.
"""
import httpx
import json
from typing import AsyncGenerator
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.services.azure_ad import get_askatt_token
from app.models.domain import Configuration
import logging

logger = logging.getLogger(__name__)


async def stream_askdocs_chat(
    configuration_id: UUID,
    message: str,
    conversation_history: list[dict],
    environment: str,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    Stream chat responses from AskDocs API using real Azure AD authentication.

    AskDocs provides domain-specific RAG responses with source attribution.

    Args:
        configuration_id: UUID of the AskDocs configuration to use
        message: User's question
        conversation_history: Previous messages in the conversation
        environment: "stage" or "production"
        db: Database session to fetch configuration

    Yields:
        SSE-formatted chunks with token, sources, usage, or end events
    """
    # Get configuration (automatically filtered by user's roles via event listener)
    stmt = select(Configuration).where(Configuration.id == configuration_id)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if not config:
        yield f"data: {json.dumps({'type': 'error', 'content': 'Configuration not found or access denied'})}\\n\\n"
        return

    # Get Azure AD access token (same as AskAT&T)
    try:
        access_token = await get_askatt_token(use_domain_scope=True)
        logger.info(f"Successfully obtained Azure AD token for AskDocs")
    except Exception as e:
        logger.error(f"Failed to get Azure AD token: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'content': 'Authentication failed'})}\\n\\n"
        return

    # Select API URL based on environment
    api_url = (
        settings.ASKDOCS_API_BASE_URL_STAGE
        if environment == "stage"
        else settings.ASKDOCS_API_BASE_URL_PRODUCTION
    )

    # Prepare the payload matching AskDocs API format
    payload = {
        "domain": config.domain.domain_key,  # Domain identifier (e.g., "SD_International")
        "config_version": config.config_key,  # Configuration key (e.g., "sim_wiki_con_v1v1")
        "query": message
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    logger.info(f"Calling AskDocs API: {api_url}")
    logger.debug(f"Domain: {payload['domain']}, Config: {payload['config_version']}")

    try:
        async with httpx.AsyncClient(verify=False, timeout=120.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"AskDocs API response received")
            logger.debug(f"Response keys: {list(result.keys())}")

            # Extract the assistant's response
            # Try multiple possible response keys
            assistant_message = None
            if "response" in result:
                assistant_message = result["response"]
            elif "answer" in result:
                assistant_message = result["answer"]
            elif "content" in result:
                assistant_message = result["content"]

            if not assistant_message:
                logger.warning(f"Unexpected API response format: {result}")
                yield f"data: {json.dumps({'type': 'error', 'content': 'Unexpected response format'})}\\n\\n"
                return

            # Stream the response token by token
            for char in assistant_message:
                yield f"data: {json.dumps({'type': 'token', 'content': char})}\\n\\n"

            # Extract and send source information if available
            sources = result.get("sources", [])
            if sources:
                # Ensure sources are in the correct format
                formatted_sources = []
                for source in sources:
                    if isinstance(source, dict):
                        formatted_sources.append({
                            "title": source.get("title", source.get("name", "Unknown")),
                            "url": source.get("url", source.get("link", "#"))
                        })

                if formatted_sources:
                    yield f"data: {json.dumps({'type': 'sources', 'sources': formatted_sources})}\\n\\n"

            # Send usage information if available
            if "usage" in result:
                usage_data = {
                    "prompt_tokens": result["usage"].get("prompt_tokens", 0),
                    "completion_tokens": result["usage"].get("completion_tokens", 0),
                    "total_tokens": result["usage"].get("total_tokens", 0)
                }
                yield f"data: {json.dumps({'type': 'usage', 'usage': usage_data})}\\n\\n"

            # Send end event
            yield f"data: {json.dumps({'type': 'end'})}\\n\\n"

    except httpx.HTTPStatusError as e:
        logger.error(f"AskDocs API error: {e.response.status_code} - {e.response.text}")

        # Try to extract error message from response
        try:
            error_data = e.response.json()
            error_msg = error_data.get("detail", error_data.get("error", f"API error: {e.response.status_code}"))
        except:
            error_msg = f"API error: {e.response.status_code}"

        yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\\n\\n"

    except httpx.TimeoutException:
        logger.error(f"AskDocs API timeout")
        yield f"data: {json.dumps({'type': 'error', 'content': 'Request timeout - API took too long to respond'})}\\n\\n"

    except Exception as e:
        logger.error(f"Error calling AskDocs API: {str(e)}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'content': f'Service error: {str(e)}'})}\\n\\n"
