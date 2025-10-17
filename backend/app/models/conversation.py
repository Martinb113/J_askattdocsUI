"""
Conversation and Message models for chat history tracking.
Stores conversations with full context (service, domain, config, environment).
"""
from uuid import uuid4
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base


class Conversation(Base):
    """Conversation model tracking chat sessions."""
    __tablename__ = "conversations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(20), index=True)  # askatt or askdocs
    domain_id: Mapped[UUID | None] = mapped_column(ForeignKey("domains.id"), nullable=True)
    configuration_id: Mapped[UUID | None] = mapped_column(ForeignKey("configurations.id"), nullable=True)
    environment: Mapped[str | None] = mapped_column(String(20), nullable=True)  # stage or production
    title: Mapped[str] = mapped_column(String(255), default="New Conversation")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # For soft delete
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, service={self.service_type}, title={self.title})>"


class Message(Base):
    """Message model storing individual chat messages."""
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), index=True)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)  # For cost tracking
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)  # sources, model used, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    conversation: Mapped[Conversation] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, content={self.content[:50]}...)>"
