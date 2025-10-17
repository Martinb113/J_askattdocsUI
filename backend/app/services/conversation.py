"""
Conversation management service for creating and retrieving chat history.
"""
from uuid import UUID
from typing import Optional
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.models.domain import Configuration
from app.core.exceptions import ResourceNotFoundError, PermissionDeniedError


async def create_conversation(
    db: AsyncSession,
    user_id: UUID,
    service_type: str,
    configuration_id: Optional[UUID] = None,
    title: Optional[str] = None
) -> Conversation:
    """
    Create a new conversation.

    Args:
        db: Database session
        user_id: User UUID
        service_type: "askatt" or "askdocs"
        configuration_id: Configuration UUID (required for askdocs)
        title: Optional conversation title

    Returns:
        Conversation: Newly created conversation
    """
    conversation = Conversation(
        user_id=user_id,
        service_type=service_type,
        configuration_id=configuration_id,
        title=title
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return conversation


async def get_conversation(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> Conversation:
    """
    Get conversation by ID (with permission check).

    Args:
        db: Database session
        conversation_id: Conversation UUID
        user_id: User UUID (for permission check)

    Returns:
        Conversation: Conversation with messages

    Raises:
        ResourceNotFoundError: If conversation not found
        PermissionDeniedError: If user doesn't own the conversation
    """
    stmt = (
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )

    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise ResourceNotFoundError("Conversation not found")

    # Permission check: user must own the conversation
    if conversation.user_id != user_id:
        raise PermissionDeniedError("You don't have access to this conversation")

    return conversation


async def list_user_conversations(
    db: AsyncSession,
    user_id: UUID,
    service_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> list[tuple[Conversation, int]]:
    """
    List user's conversations with message counts.

    Args:
        db: Database session
        user_id: User UUID
        service_type: Filter by "askatt" or "askdocs" (optional)
        limit: Maximum conversations to return
        offset: Pagination offset

    Returns:
        List of (Conversation, message_count) tuples
    """
    # Build query
    stmt = select(Conversation).where(Conversation.user_id == user_id)

    if service_type:
        stmt = stmt.where(Conversation.service_type == service_type)

    stmt = (
        stmt
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    conversations = result.scalars().all()

    # Get message counts for each conversation
    conversation_data = []
    for conv in conversations:
        count_stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conv.id)
        )
        count_result = await db.execute(count_stmt)
        message_count = count_result.scalar()

        conversation_data.append((conv, message_count))

    return conversation_data


async def add_message(
    db: AsyncSession,
    conversation_id: UUID,
    role: str,
    content: str,
    token_usage: Optional[dict] = None,
    sources: Optional[list[dict]] = None
) -> Message:
    """
    Add a message to a conversation.

    Args:
        db: Database session
        conversation_id: Conversation UUID
        role: "user" or "assistant"
        content: Message content
        token_usage: Optional token usage stats
        sources: Optional list of sources (for RAG responses)

    Returns:
        Message: Newly created message
    """
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        token_usage=token_usage,
        sources=sources
    )

    db.add(message)

    # Update conversation's updated_at timestamp
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if conversation:
        # SQLAlchemy will auto-update the updated_at field
        await db.flush()

    await db.commit()
    await db.refresh(message)

    return message


async def delete_conversation(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> None:
    """
    Delete a conversation and all its messages.

    Args:
        db: Database session
        conversation_id: Conversation UUID
        user_id: User UUID (for permission check)

    Raises:
        ResourceNotFoundError: If conversation not found
        PermissionDeniedError: If user doesn't own the conversation
    """
    # Get conversation with permission check
    conversation = await get_conversation(db, conversation_id, user_id)

    # Delete all messages first (cascade should handle this, but explicit is safer)
    await db.execute(
        delete(Message).where(Message.conversation_id == conversation_id)
    )

    # Delete conversation
    await db.delete(conversation)
    await db.commit()


async def generate_conversation_title(
    db: AsyncSession,
    conversation_id: UUID,
    first_message: str
) -> None:
    """
    Generate a title for the conversation based on the first message.

    Args:
        db: Database session
        conversation_id: Conversation UUID
        first_message: First user message in the conversation
    """
    # Simple title generation: take first 50 chars of message
    title = first_message[:50]
    if len(first_message) > 50:
        title += "..."

    # Update conversation title
    stmt = select(Conversation).where(Conversation.id == conversation_id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if conversation:
        conversation.title = title
        await db.commit()
