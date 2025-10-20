"""
AskAT&T API service using real Azure AD authentication and API format.
"""
import httpx
import json
from typing import AsyncGenerator
from app.config import settings
from app.services.azure_ad import get_askatt_token
import logging

logger = logging.getLogger(__name__)


async def stream_askatt_chat(
    message: str,
    conversation_history: list[dict],
    environment: str = "production"
) -> AsyncGenerator[str, None]:
    """
    Stream chat responses from AskAT&T API using real Azure AD authentication.

    Args:
        message: User message
        conversation_history: Previous messages in the conversation
        environment: "stage" or "production"

    Yields:
        SSE-formatted chunks with token, usage, or end events
    """
    # Get Azure AD access token
    try:
        access_token = await get_askatt_token(use_domain_scope=False)
    except Exception as e:
        logger.error(f"Failed to get Azure AD token: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'content': 'Authentication failed'})}\n\n"
        return

    # Select API URL based on environment
    api_url = (
        settings.ASKATT_API_BASE_URL_STAGE
        if environment == "stage"
        else settings.ASKATT_API_BASE_URL_PRODUCTION
    )

    # Build messages array from conversation history + new message
    messages = []
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": [
                {
                    "type": "text",
                    "text": msg["content"]
                }
            ]
        })

    # Add new user message
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": message
            }
        ]
    })

    # Prepare the payload matching the real API format
    payload = {
        "domainName": settings.ASKATT_DOMAIN_NAME,
        "modelName": settings.ASKATT_MODEL_NAME,
        "modelPayload": {
            "messages": messages,
            "max_completion_tokens": settings.ASKATT_MAX_TOKENS
        }
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    logger.info(f"Calling AskAT&T API: {api_url}")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        async with httpx.AsyncClient(verify=False, timeout=60.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            logger.info(f"AskAT&T API response received")
            logger.debug(f"Response: {json.dumps(result, indent=2)}")

            # Extract the assistant's response
            # Real API format: {"status": "success", "modelResult": {"content": "...", "response_metadata": {...}}}
            assistant_message = None

            # Try new format first (real API)
            if "status" in result and result["status"] == "success" and "modelResult" in result:
                assistant_message = result["modelResult"].get("content", "")

                # Stream the response token by token
                for char in assistant_message:
                    yield f"data: {json.dumps({'type': 'token', 'content': char})}\n\n"

                # Send usage information if available
                if "response_metadata" in result["modelResult"]:
                    token_usage = result["modelResult"]["response_metadata"].get("token_usage", {})
                    usage_data = {
                        "prompt_tokens": token_usage.get("prompt_tokens", 0),
                        "completion_tokens": token_usage.get("completion_tokens", 0),
                        "total_tokens": token_usage.get("total_tokens", 0)
                    }
                    yield f"data: {json.dumps({'type': 'usage', 'usage': usage_data})}\n\n"

            # Try old format (OpenAI-like, for compatibility)
            elif "choices" in result and len(result["choices"]) > 0:
                assistant_message = result["choices"][0]["message"]["content"]

                # Stream the response token by token
                for char in assistant_message:
                    yield f"data: {json.dumps({'type': 'token', 'content': char})}\n\n"

                # Send usage information if available
                if "usage" in result:
                    usage_data = {
                        "prompt_tokens": result["usage"].get("prompt_tokens", 0),
                        "completion_tokens": result["usage"].get("completion_tokens", 0),
                        "total_tokens": result["usage"].get("total_tokens", 0)
                    }
                    yield f"data: {json.dumps({'type': 'usage', 'usage': usage_data})}\n\n"

            else:
                # Handle unexpected response format
                logger.warning(f"Unexpected API response format: {result}")
                error_msg = result.get("error", {}).get("message", "Unexpected response format")
                yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"

            # Send end event
            yield f"data: {json.dumps({'type': 'end'})}\n\n"

    except httpx.HTTPStatusError as e:
        logger.error(f"AskAT&T API error: {e.response.status_code} - {e.response.text}")
        yield f"data: {json.dumps({'type': 'error', 'content': f'API error: {e.response.status_code}'})}\n\n"
    except Exception as e:
        logger.error(f"Error calling AskAT&T API: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
