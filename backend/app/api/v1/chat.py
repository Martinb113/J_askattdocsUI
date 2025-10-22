"""
Chat API endpoints with Server-Sent Events (SSE) streaming support.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID
import json

from app.api.deps import get_db, get_current_user, get_current_user_with_context
from app.schemas.chat import (
    ChatRequest,
    ConversationResponse,
    ConversationListItem,
    MessageResponse,
    FeedbackRequest,
    FeedbackResponse,
    ConfigurationResponse,
    DomainResponse,
)
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.feedback import Feedback
from app.models.domain import Configuration, Domain
from app.services.conversation import (
    create_conversation,
    get_conversation,
    list_user_conversations,
    add_message,
    delete_conversation,
    generate_conversation_title,
)
from app.services.askatt_mock import stream_askatt_chat as stream_askatt_chat_mock
from app.services.askatt import stream_askatt_chat as stream_askatt_chat_real
from app.services.askdocs_mock import stream_askdocs_chat as stream_askdocs_chat_mock
from app.services.askdocs import stream_askdocs_chat as stream_askdocs_chat_real
from app.core.exceptions import ResourceNotFoundError, PermissionDeniedError, ValidationError
from sqlalchemy import select
from app.config import settings

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/askatt", response_class=StreamingResponse)
async def chat_askatt(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with AskAT&T (general OpenAI chat) using Server-Sent Events streaming.

    **Request Body:**
    - `message`: User message (1-4000 characters)
    - `conversation_id`: Optional existing conversation ID

    **Response:**
    - Streams token-by-token response using SSE format
    - Event types: `token`, `usage`, `end`

    **Example:**
    ```bash
    curl -X POST http://localhost:8000/api/v1/chat/askatt \\
      -H "Authorization: Bearer <token>" \\
      -H "Content-Type: application/json" \\
      -d '{"message": "Hello, how are you?"}' \\
      --no-buffer
    ```

    **SSE Event Format:**
    ```
    data: {"type": "token", "content": "H"}
    data: {"type": "token", "content": "e"}
    ...
    data: {"type": "usage", "usage": {"prompt_tokens": 10, "completion_tokens": 50, "total_tokens": 60}}
    data: {"type": "end"}
    ```
    """
    async def stream_response():
        # Get or create conversation
        conversation_id = request.conversation_id

        if conversation_id:
            # Verify conversation exists and user owns it
            try:
                conversation = await get_conversation(db, conversation_id, current_user.id)
            except (ResourceNotFoundError, PermissionDeniedError) as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                return
        else:
            # Create new conversation
            conversation = await create_conversation(
                db=db,
                user_id=current_user.id,
                service_type="askatt"
            )
            conversation_id = conversation.id

            # Send conversation_id to client
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': str(conversation_id)})}\n\n"

        # Save user message
        await add_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        # Generate title if first message
        if not conversation.title:
            await generate_conversation_title(db, conversation_id, request.message)

        # Get conversation history for context
        conversation_data = await get_conversation(db, conversation_id, current_user.id)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_data.messages[:-1]  # Exclude the just-added user message
        ]

        # Stream AI response (use real or mock based on settings)
        assistant_message = ""
        usage_data = None

        stream_func = stream_askatt_chat_mock if settings.USE_MOCK_ASKATT else stream_askatt_chat_real

        async for chunk in stream_func(
            message=request.message,
            conversation_history=conversation_history,
            environment="production"
        ):
            # Forward chunk to client
            yield chunk

            # Parse chunk to build assistant message
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if data["type"] == "token":
                        assistant_message += data["content"]
                    elif data["type"] == "usage":
                        usage_data = data["usage"]
                except json.JSONDecodeError:
                    pass

        # Save assistant message
        message = await add_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message,
            token_usage=usage_data
        )

        # Send message_id to client so feedback can be attached to the real message
        yield f"data: {json.dumps({'type': 'message_id', 'message_id': str(message.id)})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")


@router.post("/askdocs", response_class=StreamingResponse)
async def chat_askdocs(
    request: ChatRequest,
    current_user: User = Depends(get_current_user_with_context),  # CRITICAL: use context version
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with AskDocs (domain-specific RAG chat) using Server-Sent Events streaming.

    **IMPORTANT:** Requires `configuration_id` in request. User must have role access to the configuration.

    **Request Body:**
    - `message`: User message (1-4000 characters)
    - `configuration_id`: **Required** - AskDocs configuration ID
    - `conversation_id`: Optional existing conversation ID

    **Response:**
    - Streams token-by-token response using SSE format
    - Event types: `token`, `sources`, `usage`, `end`

    **Example:**
    ```bash
    curl -X POST http://localhost:8000/api/v1/chat/askdocs \\
      -H "Authorization: Bearer <token>" \\
      -H "Content-Type: application/json" \\
      -d '{"message": "How do I reset my password?", "configuration_id": "uuid-here"}' \\
      --no-buffer
    ```
    """
    # Validate configuration_id is provided
    if not request.configuration_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="configuration_id is required for AskDocs chat"
        )

    async def stream_response():
        # Verify configuration exists and user has access
        # (automatic filtering via role-based event listener)
        stmt = select(Configuration).where(Configuration.id == request.configuration_id)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()

        if not config:
            yield f"data: {json.dumps({'type': 'error', 'content': 'Configuration not found or access denied'})}\n\n"
            return

        # Get or create conversation
        conversation_id = request.conversation_id

        if conversation_id:
            try:
                conversation = await get_conversation(db, conversation_id, current_user.id)
                # Verify conversation matches configuration
                if conversation.configuration_id != request.configuration_id:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Conversation configuration mismatch'})}\n\n"
                    return
            except (ResourceNotFoundError, PermissionDeniedError) as e:
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
                return
        else:
            # Create new conversation
            conversation = await create_conversation(
                db=db,
                user_id=current_user.id,
                service_type="askdocs",
                configuration_id=request.configuration_id
            )
            conversation_id = conversation.id

            # Send conversation_id to client
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': str(conversation_id)})}\n\n"

        # Save user message
        await add_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        # Generate title if first message
        if not conversation.title:
            await generate_conversation_title(db, conversation_id, request.message)

        # Get conversation history
        conversation_data = await get_conversation(db, conversation_id, current_user.id)
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_data.messages[:-1]
        ]

        # Stream AI response with RAG (use real or mock based on settings)
        assistant_message = ""
        usage_data = None
        sources_data = None

        stream_func = stream_askdocs_chat_mock if settings.USE_MOCK_ASKDOCS else stream_askdocs_chat_real

        async for chunk in stream_func(
            configuration_id=request.configuration_id,
            message=request.message,
            conversation_history=conversation_history,
            environment=config.environment,
            db=db
        ):
            # Forward chunk to client
            yield chunk

            # Parse chunk
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if data["type"] == "token":
                        assistant_message += data["content"]
                    elif data["type"] == "usage":
                        usage_data = data["usage"]
                    elif data["type"] == "sources":
                        sources_data = data["sources"]
                except json.JSONDecodeError:
                    pass

        # Save assistant message with sources
        message = await add_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message,
            token_usage=usage_data,
            sources=sources_data
        )

        # Send message_id to client so feedback can be attached to the real message
        yield f"data: {json.dumps({'type': 'message_id', 'message_id': str(message.id)})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(
    service_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List user's conversations.

    **Query Parameters:**
    - `service_type`: Filter by "askatt" or "askdocs"
    - `limit`: Max conversations to return (default 50)
    - `offset`: Pagination offset (default 0)

    **Returns:**
    - List of conversation summaries with message counts
    """
    conversations_data = await list_user_conversations(
        db=db,
        user_id=current_user.id,
        service_type=service_type,
        limit=limit,
        offset=offset
    )

    return [
        ConversationListItem(
            id=conv.id,
            service_type=conv.service_type,
            title=conv.title,
            configuration_id=conv.configuration_id,
            message_count=count,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        )
        for conv, count in conversations_data
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_detail(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get conversation with full message history.

    **Returns:**
    - Conversation with all messages

    **Errors:**
    - `404`: Conversation not found
    - `403`: No access to this conversation
    """
    try:
        conversation = await get_conversation(db, conversation_id, current_user.id)

        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            service_type=conversation.service_type,
            configuration_id=conversation.configuration_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                MessageResponse.from_orm(msg)
                for msg in conversation.messages
            ]
        )

    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_endpoint(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its messages.

    **Errors:**
    - `404`: Conversation not found
    - `403`: No access to this conversation
    """
    try:
        await delete_conversation(db, conversation_id, current_user.id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/configurations", response_model=list[ConfigurationResponse])
async def list_configurations(
    environment: Optional[str] = None,
    current_user: User = Depends(get_current_user_with_context),  # CRITICAL: use context version
    db: AsyncSession = Depends(get_db)
):
    """
    List AskDocs configurations accessible to the current user.

    **IMPORTANT:** Only returns configurations the user has role-based access to.

    **Query Parameters:**
    - `environment`: Filter by "stage" or "production"

    **Returns:**
    - List of configurations with domain information
    """
    stmt = (
        select(Configuration)
        .where(Configuration.is_active == True)
        .options(selectinload(Configuration.domain))
    )

    if environment:
        stmt = stmt.where(Configuration.environment == environment)

    result = await db.execute(stmt)
    configurations = result.scalars().all()

    return [
        ConfigurationResponse(
            id=config.id,
            domain_id=config.domain_id,
            config_key=config.config_key,
            display_name=config.display_name,
            description=config.description,
            environment=config.environment,
            is_active=config.is_active,
            domain=DomainResponse(
                id=config.domain.id,
                domain_key=config.domain.domain_key,
                display_name=config.domain.display_name,
                description=config.domain.description
            )
        )
        for config in configurations
    ]


@router.post("/messages/{message_id}/feedback", response_model=FeedbackResponse)
async def submit_message_feedback(
    message_id: UUID,
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit feedback (rating + optional comment) for an assistant message.

    **Path Parameters:**
    - `message_id`: UUID of the message to rate

    **Request Body:**
    - `rating`: Integer 1-5
    - `comment`: Optional text comment (max 1000 chars)

    **Returns:**
    - Created feedback record

    **Errors:**
    - `404`: Message not found
    - `403`: No access to this message
    """
    # Verify message exists and user has access
    stmt = select(Message).where(Message.id == message_id)
    result = await db.execute(stmt)
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    # Verify user owns the conversation
    stmt = select(Conversation).where(Conversation.id == message.conversation_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Convert numeric rating (1-5) to up/down format
    # 4-5 = up (positive), 1-3 = down (negative)
    rating_value = "up" if request.rating >= 4 else "down"

    # Create feedback with all required fields
    feedback = Feedback(
        message_id=message_id,
        user_id=current_user.id,
        conversation_id=conversation.id,
        rating=rating_value,
        comment=request.comment,
        service_type=conversation.service_type,
        domain_id=None,  # Will be populated if configuration exists
        configuration_id=conversation.configuration_id,
        environment=None  # Will be populated if configuration exists
    )

    # If conversation has a configuration, get domain and environment
    if conversation.configuration_id:
        from app.models.domain import Configuration
        stmt = select(Configuration).where(Configuration.id == conversation.configuration_id)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        if config:
            feedback.domain_id = config.domain_id
            feedback.environment = config.environment

    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return FeedbackResponse(
        id=feedback.id,
        message_id=feedback.message_id,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at
    )
