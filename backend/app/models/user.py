"""
User and Role models with many-to-many relationship.
Implements role-based access control (RBAC).
"""
from uuid import uuid4
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.database import Base

if TYPE_CHECKING:
    from app.models.domain import Configuration

# Association table for User-Roles (many-to-many)
# Users can have multiple roles, roles can be assigned to multiple users
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid4),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), nullable=False),
    Column("assigned_at", DateTime, default=datetime.utcnow),
    Column("assigned_by", UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Admin who assigned
)


class User(Base):
    """User model with AT&T ID authentication."""
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    attid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships with lazy="selectin" for async - CRITICAL to prevent greenlet errors
    # Specify primaryjoin to disambiguate which user_id to use (user_id, not assigned_by)
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        primaryjoin="User.id == user_roles.c.user_id",
        secondaryjoin="Role.id == user_roles.c.role_id",
        back_populates="users",
        lazy="selectin"  # CRITICAL: loads eagerly to avoid async issues
    )

    def __repr__(self) -> str:
        return f"<User(attid={self.attid}, email={self.email})>"


class Role(Base):
    """Role model for role-based access control."""
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships with lazy="selectin" for async
    # Specify primaryjoin to disambiguate which user_id to use (user_id, not assigned_by)
    users: Mapped[list[User]] = relationship(
        secondary=user_roles,
        primaryjoin="Role.id == user_roles.c.role_id",
        secondaryjoin="User.id == user_roles.c.user_id",
        back_populates="roles",
        lazy="selectin"
    )

    configurations: Mapped[list["Configuration"]] = relationship(
        secondary="role_configuration_access",
        back_populates="roles",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Role(name={self.name})>"
