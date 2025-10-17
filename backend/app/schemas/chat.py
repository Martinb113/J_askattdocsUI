"""
Pydantic schemas for chat endpoints.
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class ChatRequest(BaseModel):
    """Chat message request."""
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (optional)")
    configuration_id: Optional[UUID] = Field(None, description="AskDocs configuration ID (for RAG chat)")


class MessageResponse(BaseModel):
    """Single message response."""
    id: UUID
    conversation_id: UUID
    role: str  # "user" or "assistant"
    content: str
    token_usage: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation with messages."""
    id: UUID
    user_id: UUID
    service_type: str  # "askatt" or "askdocs"
    configuration_id: Optional[UUID] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ConversationListItem(BaseModel):
    """Conversation summary for list view."""
    id: UUID
    service_type: str
    title: Optional[str] = None
    configuration_id: Optional[UUID] = None
    message_count: int = Field(default=0)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FeedbackRequest(BaseModel):
    """User feedback on a message."""
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    comment: Optional[str] = Field(None, max_length=1000, description="Optional comment")


class FeedbackResponse(BaseModel):
    """Feedback response."""
    id: UUID
    message_id: UUID
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConfigurationResponse(BaseModel):
    """AskDocs configuration response."""
    id: UUID
    domain_id: UUID
    config_key: str
    display_name: str
    description: Optional[str] = None
    environment: str
    is_active: bool
    domain: "DomainResponse"

    class Config:
        from_attributes = True


class DomainResponse(BaseModel):
    """AskDocs domain response."""
    id: UUID
    domain_key: str
    display_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
