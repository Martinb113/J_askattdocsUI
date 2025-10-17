"""
Domain and Configuration models for AskDocs integration.
Implements configuration access control via many-to-many with roles.
"""
from uuid import uuid4
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Table, Column, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import Role


# Association table for Role-Configuration access (many-to-many)
# Roles can access multiple configurations, configurations can be accessed by multiple roles
role_configuration_access = Table(
    "role_configuration_access",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column("configuration_id", ForeignKey("configurations.id", ondelete="CASCADE"), nullable=False),
    Column("granted_by", UUID(as_uuid=True), ForeignKey("users.id"), nullable=True),  # Admin who granted
    Column("granted_at", DateTime, default=datetime.utcnow)
)


class Domain(Base):
    """Domain model representing AskDocs knowledge domains."""
    __tablename__ = "domains"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    domain_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    configurations: Mapped[list["Configuration"]] = relationship(
        back_populates="domain",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Domain(domain_key={self.domain_key})>"


class Configuration(Base):
    """Configuration model representing specific versions/configs within a domain."""
    __tablename__ = "configurations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    domain_id: Mapped[UUID] = mapped_column(ForeignKey("domains.id"), nullable=False)
    config_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    environment: Mapped[str] = mapped_column(String(20), default="production", index=True)  # stage or production
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)  # Additional config settings
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    domain: Mapped[Domain] = relationship(back_populates="configurations", lazy="selectin")

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_configuration_access,
        back_populates="configurations",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Configuration(config_key={self.config_key}, environment={self.environment})>"
