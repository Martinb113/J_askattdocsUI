"""
MOCK AskAT&T service for local development.
Simulates streaming responses from the real AskAT&T API.

This allows you to develop and test the full application without needing
access to the actual AskAT&T endpoints on the corporate intranet.
"""
from typing import AsyncGenerator
import json
import asyncio
import random

# Sample responses to simulate AI chat
MOCK_RESPONSES = [
    "Hello! I'm a mock AI assistant simulating the AskAT&T service. How can I help you today?",
    "That's a great question! In a production environment, I would connect to the actual AskAT&T API to provide real-time answers using GPT-4.",
    "I'm currently running in MOCK mode for local development. When deployed with real Azure AD credentials and AskAT&T API access, I'll provide intelligent responses to your queries.",
    "This mock service demonstrates token-by-token streaming, which is how the real service will work. Each character appears one at a time!",
    "You can test all the features: role-based access, conversation history, feedback collection, and more - all without needing corporate network access.",
]


async def stream_askatt_chat_mock(
    message: str,
    conversation_history: list[dict],
    environment: str = "production"
) -> AsyncGenerator[str, None]:
    """
    Mock AskAT&T streaming chat service.

    This simulates the real AskAT&T API response format with:
    - Token-by-token streaming (SSE format)
    - Usage statistics
    - Proper error handling

    Args:
        message: User's message
        conversation_history: Previous conversation messages
        environment: "stage" or "production" (not used in mock)

    Yields:
        SSE-formatted events: data: {json}\\n\\n
    """
    # Select a random mock response or generate based on message
    if "hello" in message.lower() or "hi" in message.lower():
        response_text = MOCK_RESPONSES[0]
    elif "?" in message:
        response_text = MOCK_RESPONSES[1]
    elif len(conversation_history) > 0:
        response_text = MOCK_RESPONSES[2]
    else:
        response_text = random.choice(MOCK_RESPONSES)

    # Add context-aware response
    if "test" in message.lower():
        response_text = "Testing the mock AskAT&T service! Everything is working correctly. " + response_text

    # Simulate token-by-token streaming
    for char in response_text:
        yield f"data: {json.dumps({'type': 'token', 'content': char})}\n\n"
        await asyncio.sleep(0.01)  # Simulate network delay

    # Send mock usage statistics
    mock_usage = {
        "prompt_tokens": len(message.split()),
        "completion_tokens": len(response_text.split()),
        "total_tokens": len(message.split()) + len(response_text.split())
    }

    yield f"data: {json.dumps({'type': 'usage', 'usage': mock_usage})}\n\n"

    # Send end event
    yield f"data: {json.dumps({'type': 'end'})}\n\n"


async def stream_askatt_chat(
    message: str,
    conversation_history: list[dict],
    environment: str = "production"
) -> AsyncGenerator[str, None]:
    """
    Wrapper function that matches the real service interface.

    In production, this would be replaced with the real AskAT&T integration.
    For now, it calls the mock service.
    """
    async for chunk in stream_askatt_chat_mock(message, conversation_history, environment):
        yield chunk
