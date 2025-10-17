"""
MOCK AskDocs service for local development.
Simulates streaming RAG responses with sources from the real AskDocs API.

This allows you to develop and test the full application without needing
access to the actual AskDocs endpoints on the corporate intranet.
"""
from typing import AsyncGenerator
from uuid import UUID
import json
import asyncio
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.domain import Configuration

# Sample RAG responses with sources
MOCK_RAG_RESPONSES = {
    "password": {
        "answer": "To reset your password, follow these steps:\n\n1. Go to the AT&T login page\n2. Click 'Forgot Password'\n3. Enter your AT&T ID\n4. Follow the verification steps sent to your registered email\n5. Create a new secure password\n\nYour password must contain at least 8 characters, including uppercase, lowercase, numbers, and special characters.",
        "sources": [
            {"title": "AT&T Password Reset Guide", "url": "https://att.com/support/password-reset"},
            {"title": "Account Security Best Practices", "url": "https://att.com/security/passwords"},
        ]
    },
    "billing": {
        "answer": "You can view your billing information by:\n\n1. Logging into your AT&T account\n2. Navigating to 'Billing & Payments'\n3. Selecting 'View Current Bill'\n\nYour bill includes charges for your service plan, device payments, and any additional features or overages.",
        "sources": [
            {"title": "Understanding Your AT&T Bill", "url": "https://att.com/support/billing"},
            {"title": "Payment Options", "url": "https://att.com/support/payment-methods"},
        ]
    },
    "support": {
        "answer": "AT&T customer support is available 24/7 through multiple channels:\n\n- Phone: Call 1-800-331-0500\n- Live Chat: Available on att.com\n- myAT&T App: Message support directly\n- AT&T Stores: Find a location near you\n\nFor technical support, you can also visit our online troubleshooting guides.",
        "sources": [
            {"title": "Contact AT&T Support", "url": "https://att.com/support/contact"},
            {"title": "Self-Service Help", "url": "https://att.com/support/self-service"},
        ]
    },
}


async def stream_askdocs_chat_mock(
    configuration_id: UUID,
    message: str,
    conversation_history: list[dict],
    environment: str,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    Mock AskDocs streaming RAG chat service.

    This simulates the real AskDocs API response format with:
    - Token-by-token streaming
    - Source attribution
    - Domain/configuration-specific responses
    - Usage statistics

    Args:
        configuration_id: UUID of the configuration to use
        message: User's question
        conversation_history: Previous conversation messages
        environment: "stage" or "production"
        db: Database session

    Yields:
        SSE-formatted events: data: {json}\\n\\n
    """
    # Get configuration (automatically filtered by user's roles via event listener)
    stmt = select(Configuration).where(Configuration.id == configuration_id)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if not config:
        yield f"data: {json.dumps({'type': 'error', 'content': 'Configuration not found or access denied'})}\\n\\n"
        return

    # Select appropriate mock response based on message content
    message_lower = message.lower()

    if "password" in message_lower or "reset" in message_lower:
        mock_data = MOCK_RAG_RESPONSES["password"]
    elif "bill" in message_lower or "payment" in message_lower or "charge" in message_lower:
        mock_data = MOCK_RAG_RESPONSES["billing"]
    elif "support" in message_lower or "help" in message_lower or "contact" in message_lower:
        mock_data = MOCK_RAG_RESPONSES["support"]
    else:
        # Generic response
        mock_data = {
            "answer": f"Based on your question about '{message}' and the {config.config_key} configuration, I would retrieve relevant documents from the {config.domain.domain_key} knowledge base and provide a detailed answer with source citations. This is a MOCK response for local development.",
            "sources": [
                {"title": f"{config.domain.display_name} Documentation", "url": "https://att.com/support/docs"},
                {"title": "Knowledge Base Article", "url": "https://att.com/kb/12345"},
            ]
        }

    # Add environment indicator to answer
    env_note = f"\\n\\n*[MOCK {environment.upper()} environment - Config: {config.config_key}]*"
    answer_text = mock_data["answer"] + env_note

    # Stream answer token by token
    for char in answer_text:
        yield f"data: {json.dumps({'type': 'token', 'content': char})}\\n\\n"
        await asyncio.sleep(0.01)  # Simulate network delay

    # Send sources
    yield f"data: {json.dumps({'type': 'sources', 'sources': mock_data['sources']})}\\n\\n"

    # Send mock usage statistics
    mock_usage = {
        "prompt_tokens": len(message.split()) + 50,  # Account for RAG context
        "completion_tokens": len(answer_text.split()),
        "total_tokens": len(message.split()) + len(answer_text.split()) + 50
    }

    yield f"data: {json.dumps({'type': 'usage', 'usage': mock_usage})}\\n\\n"

    # Send end event
    yield f"data: {json.dumps({'type': 'end'})}\\n\\n"


async def stream_askdocs_chat(
    configuration_id: UUID,
    message: str,
    conversation_history: list[dict],
    environment: str,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    Wrapper function that matches the real service interface.

    In production, this would be replaced with the real AskDocs integration.
    For now, it calls the mock service.
    """
    async for chunk in stream_askdocs_chat_mock(
        configuration_id, message, conversation_history, environment, db
    ):
        yield chunk
