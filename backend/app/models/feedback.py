"""
Feedback and TokenUsageLog models for quality tracking and cost analysis.
"""
from uuid import uuid4
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base


class Feedback(Base):
    """Feedback model for per-message quality ratings."""
    __tablename__ = "feedback"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    message_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id"), nullable=False, index=True)
    rating: Mapped[str] = mapped_column(String(10), nullable=False)  # up or down
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)  # Optional user explanation
    service_type: Mapped[str] = mapped_column(String(20), index=True)  # askatt or askdocs
    domain_id: Mapped[UUID | None] = mapped_column(ForeignKey("domains.id"), nullable=True)
    configuration_id: Mapped[UUID | None] = mapped_column(ForeignKey("configurations.id"), nullable=True)
    environment: Mapped[str | None] = mapped_column(String(20), nullable=True)  # stage or production
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        CheckConstraint("rating IN ('up', 'down')", name="check_rating_values"),
        # Unique constraint: one feedback per user per message
        # Commented out for now - uncomment if you want to prevent multiple feedback per message
        # UniqueConstraint("user_id", "message_id", name="unique_user_message_feedback")
    )

    def __repr__(self) -> str:
        return f"<Feedback(id={self.id}, rating={self.rating}, message_id={self.message_id})>"


class TokenUsageLog(Base):
    """Token usage log for cost tracking (backend only, not user-facing)."""
    __tablename__ = "token_usage_log"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    message_id: Mapped[UUID] = mapped_column(ForeignKey("messages.id"), nullable=False, index=True)
    service_type: Mapped[str] = mapped_column(String(20), index=True)  # askatt or askdocs
    model_name: Mapped[str] = mapped_column(String(100))  # gpt-4o, gpt-3.5-turbo, etc.
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)  # Optional cost calculation
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<TokenUsageLog(id={self.id}, model={self.model_name}, total_tokens={self.total_tokens})>"
