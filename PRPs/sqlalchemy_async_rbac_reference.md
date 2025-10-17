# SQLAlchemy 2.0 Async Patterns for FastAPI with RBAC

## Complete Reference Documentation

This document provides comprehensive SQLAlchemy 2.0 async patterns for FastAPI applications implementing role-based access control (RBAC) with PostgreSQL.

---

## Table of Contents

1. [Async Database Setup](#1-async-database-setup)
2. [Model Definitions with UUID](#2-model-definitions-with-uuid)
3. [Many-to-Many Relationships](#3-many-to-many-relationships)
4. [Role-Based Filtering Patterns](#4-role-based-filtering-patterns)
5. [Async Query Patterns](#5-async-query-patterns)
6. [Alembic Configuration](#6-alembic-configuration)
7. [Best Practices](#7-best-practices)
8. [Common Gotchas](#8-common-gotchas)

---

## 1. Async Database Setup

### Official Documentation
- **SQLAlchemy AsyncIO Extension**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **PostgreSQL Dialect**: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html

### 1.1 Engine Configuration with Connection Pooling

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

# Production setup with connection pooling
async_engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost:5432/dbname",
    echo=True,  # Set to False in production
    pool_size=20,           # Number of connections to maintain
    max_overflow=10,        # Additional connections allowed beyond pool_size
    pool_recycle=3600,      # Recycle connections after 1 hour (prevents stale connections)
    pool_pre_ping=True,     # Test connections before use (reliability)
    pool_timeout=30,        # Timeout for acquiring connection from pool
)

# Alternative: NullPool for serverless or multiple event loops
async_engine_nullpool = create_async_engine(
    "postgresql+asyncpg://user:password@localhost:5432/dbname",
    poolclass=NullPool,  # No connection pooling - creates new connection each time
    echo=False,
)
```

**Key Parameters Explained:**
- `pool_size=20`: Core pool size - connections kept alive even when idle
- `max_overflow=10`: Additional connections created during peak load (total = 30)
- `pool_recycle=3600`: Prevents "MySQL has gone away" type errors
- `pool_pre_ping=True`: Validates connection health before use
- `NullPool`: Use for AWS Lambda, multiple async event loops, or testing

### 1.2 Async Session Configuration

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    AsyncAttrs
)
from sqlalchemy.orm import DeclarativeBase

# Base class with async attribute support
class Base(AsyncAttrs, DeclarativeBase):
    """
    AsyncAttrs enables awaitable attribute access for relationships.
    Required for: await user.addresses
    """
    pass

# Session factory (create once, reuse throughout application)
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # CRITICAL: Prevents implicit I/O after commit in async
    autoflush=False,         # Explicit control over when SQL is emitted
    autocommit=False,        # Always use transactions explicitly
)

# Usage in application
async def get_data():
    async with async_session_factory() as session:
        # Use session here
        result = await session.execute(select(User))
        return result.scalars().all()
```

**Critical Configuration:**
- `expire_on_commit=False`: **MUST BE SET** for async - prevents "greenlet" errors
- `AsyncAttrs` mixin: Enables `await user.addresses` syntax for relationships
- `autoflush=False`: Recommended for explicit transaction control

### 1.3 FastAPI Dependency Injection Pattern

```python
from typing import AsyncGenerator
from fastapi import Depends
from functools import lru_cache

# Singleton engine pattern
@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Cache engine instance - create only once."""
    return create_async_engine(
        "postgresql+asyncpg://user:pass@localhost:5432/db",
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )

# Session dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides AsyncSession.
    Automatically handles session lifecycle (creation + cleanup).
    """
    async with async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        class_=AsyncSession
    )() as session:
        try:
            yield session
            await session.commit()  # Auto-commit on success
        except Exception:
            await session.rollback()  # Auto-rollback on error
            raise
        finally:
            await session.close()

# Usage in FastAPI routes
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user
```

**Performance Notes:**
- Async DB queries handle **3-5x more requests/sec** vs sync (per benchmarks)
- One session per request - **never reuse sessions across requests**
- `lru_cache` for engine prevents creating multiple engine instances

---

## 2. Model Definitions with UUID

### Official Documentation
- **UUID Types**: https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#postgresql-uuid
- **Mapped Column**: https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#mapped-column

### 2.1 PostgreSQL UUID Primary Keys

```python
from uuid import UUID, uuid4
from sqlalchemy import func, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    # Option 1: Python-side UUID generation
    # UUID available immediately after object creation
    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4  # Note: Pass function, not uuid4()
    )

    # Option 2: Database-side UUID generation (PostgreSQL gen_random_uuid())
    # More efficient, but UUID only available after INSERT
    # id: Mapped[UUID] = mapped_column(
    #     primary_key=True,
    #     server_default=func.gen_random_uuid()
    # )

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
```

### 2.2 Dataclass Pattern (Immediate UUID Access)

```python
from sqlalchemy.orm import MappedAsDataclass

class User(MappedAsDataclass, Base):
    """
    Dataclass pattern: UUID generated in __init__, available immediately.
    Use when you need UUID before database INSERT.
    """
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default_factory=uuid4,  # Use default_factory for dataclass
        init=False  # Don't require in __init__
    )
    username: Mapped[str]
    email: Mapped[str]

# Usage
user = User(username="john", email="john@example.com")
print(user.id)  # UUID available immediately (not None)
```

### 2.3 Choosing UUID Generation Strategy

| Strategy | When to Use | Pros | Cons |
|----------|-------------|------|------|
| `default=uuid4` | General use, FastAPI | Simple, immediate access | Extra function call overhead |
| `default_factory=uuid4` | Dataclass models | UUID in `__init__` | Requires dataclass pattern |
| `server_default=func.gen_random_uuid()` | High-performance inserts | DB handles generation, fast | UUID not available until after INSERT |

**Recommendation for FastAPI + RBAC:**
- Use `default=uuid4` for simplicity and immediate ID access
- Use `server_default` for bulk imports or high-throughput scenarios

---

## 3. Many-to-Many Relationships

### Official Documentation
- **Basic Relationships**: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many

### 3.1 Association Table Pattern (Simple M2M)

```python
from sqlalchemy import Table, Column, ForeignKey
from typing import List

# Association table for User <-> Role (many-to-many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("assigned_at", DateTime(timezone=True), server_default=func.now()),
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True)

    # Many-to-many relationship to Role
    roles: Mapped[List["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin"  # Critical for async - prevents lazy loading errors
    )

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))

    # Bidirectional relationship
    users: Mapped[List["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin"
    )
```

**Key Configuration:**
- `secondary=user_roles`: Points to association table
- `back_populates`: Creates bidirectional relationship
- `lazy="selectin"`: **Required for async** - prevents "greenlet" errors
- `ondelete="CASCADE"`: Automatically cleans up when parent deleted

### 3.2 Association Object Pattern (M2M with Extra Data)

```python
from datetime import datetime

class RoleConfiguration(Base):
    """
    Association object: Adds metadata to role assignments.
    Use when you need extra fields beyond just the relationship.
    """
    __tablename__ = "role_configurations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"))
    configuration_id: Mapped[UUID] = mapped_column(
        ForeignKey("configurations.id", ondelete="CASCADE")
    )

    # Extra fields (this is why we use association object)
    access_level: Mapped[int] = mapped_column(default=1)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    granted_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships to parent tables
    role: Mapped["Role"] = relationship(back_populates="configurations")
    configuration: Mapped["Configuration"] = relationship(back_populates="roles")
    granter: Mapped["User"] = relationship()

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    # Relationship to association object
    configurations: Mapped[List["RoleConfiguration"]] = relationship(
        back_populates="role",
        lazy="selectin"
    )

class Configuration(Base):
    __tablename__ = "configurations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))

    # Relationship to association object
    roles: Mapped[List["RoleConfiguration"]] = relationship(
        back_populates="configuration",
        lazy="selectin"
    )
```

**When to Use Association Object:**
- Need timestamps (who assigned, when, expiration)
- Access levels, permissions, or scopes
- Audit trail for relationship changes
- Conditional relationships (active/inactive)

### 3.3 Querying Many-to-Many Relationships

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

async def get_user_with_roles(user_id: UUID, db: AsyncSession):
    """Fetch user with all roles (N+1 query avoided)."""
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles))  # Eager load roles
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_users_by_role(role_name: str, db: AsyncSession):
    """Find all users with specific role."""
    stmt = (
        select(User)
        .join(User.roles)
        .where(Role.name == role_name)
        .options(selectinload(User.roles))
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def check_user_has_role(user_id: UUID, role_name: str, db: AsyncSession) -> bool:
    """Efficiently check if user has specific role."""
    stmt = (
        select(User)
        .join(User.roles)
        .where(User.id == user_id, Role.name == role_name)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None
```

---

## 4. Role-Based Filtering Patterns

### Official Documentation
- **Query Events**: https://docs.sqlalchemy.org/en/20/orm/session_events.html#do-orm-execute
- **with_loader_criteria**: https://docs.sqlalchemy.org/en/20/orm/queryguide/api.html#sqlalchemy.orm.with_loader_criteria

### 4.1 Global Role-Based Filtering with Event Listeners

```python
from sqlalchemy import event, true
from sqlalchemy.orm import Session, with_loader_criteria
from contextvars import ContextVar
from enum import Enum

# Context variable to store current user's roles (thread-safe in async)
current_user_roles: ContextVar[set[str]] = ContextVar("current_user_roles", default=set())

class UserRole(str, Enum):
    ADMIN = "admin"
    PAID_USER = "paid_user"
    FREE_USER = "free_user"

# Mixin for entities requiring role-based filtering
class HasAccessControl:
    """Mixin for models with role-based access control."""
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_paid_access: Mapped[bool] = mapped_column(Boolean, default=False)

class Document(HasAccessControl, Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str]
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["User"] = relationship()

# Event listener for automatic filtering
@event.listens_for(Session, "do_orm_execute")
def apply_role_based_filtering(execute_state):
    """
    Automatically applies role-based filters to ALL queries.
    Runs before every SELECT, UPDATE, DELETE operation.
    """
    # Skip for column loads and relationship loads
    if (
        execute_state.is_column_load
        or execute_state.is_relationship_load
    ):
        return

    # Allow bypassing filter with execution option
    if execute_state.execution_options.get("include_filtered", False):
        return

    # Get current user's roles from context
    roles = current_user_roles.get()

    # Apply filters based on role
    if UserRole.ADMIN in roles:
        # Admin: Only filter deleted items
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                HasAccessControl,
                lambda cls: cls.is_deleted == False,
                include_aliases=True,
            )
        )
    elif UserRole.PAID_USER in roles:
        # Paid users: See all non-deleted, public + paid content
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                HasAccessControl,
                lambda cls: (
                    (cls.is_deleted == False)
                    & (cls.is_public == True)
                ),
                include_aliases=True,
            )
        )
    else:  # FREE_USER or no role
        # Free users: Only non-deleted, public, non-paid content
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                HasAccessControl,
                lambda cls: (
                    (cls.is_deleted == False)
                    & (cls.is_public == True)
                    & (cls.requires_paid_access == False)
                ),
                include_aliases=True,
            )
        )
```

**How it Works:**
1. `do_orm_execute` event fires **before every ORM query**
2. `with_loader_criteria` adds WHERE clauses automatically
3. `include_aliases=True`: Applies to JOINed tables with aliases
4. Filters propagate to **all relationship loads** (lazy, selectin, joined)

### 4.2 FastAPI Integration with Context Variables

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user_roles(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> set[str]:
    """
    Extract user roles from JWT token and set in context.
    """
    token = credentials.credentials
    # Decode JWT (implementation depends on your auth library)
    user_id = decode_jwt_token(token)  # Your JWT decode logic

    # Fetch user with roles
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )

    # Extract role names and set in context
    role_names = {role.name for role in user.roles}
    current_user_roles.set(role_names)

    return role_names

# FastAPI route with automatic filtering
@app.get("/documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    roles: set[str] = Depends(get_current_user_roles)
):
    """
    Returns documents filtered by user's role.
    Filtering happens automatically via event listener.
    """
    stmt = select(Document)
    result = await db.execute(stmt)
    documents = result.scalars().all()

    # Documents already filtered based on roles in context
    return documents

# Bypass filtering for admin operations
@app.get("/admin/documents/all")
async def list_all_documents_admin(
    db: AsyncSession = Depends(get_db),
    roles: set[str] = Depends(get_current_user_roles)
):
    """Admin-only: See ALL documents including deleted."""
    if UserRole.ADMIN not in roles:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Bypass automatic filtering
    stmt = select(Document).execution_options(include_filtered=True)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### 4.3 Per-Query Filtering (Without Event Listener)

```python
async def get_documents_for_user(
    user_id: UUID,
    db: AsyncSession
) -> list[Document]:
    """
    Manually filter documents based on user's roles.
    Use when you don't want global event listener.
    """
    # Fetch user with roles
    user_stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles))
    )
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one()

    role_names = {role.name for role in user.roles}

    # Build query with role-based filters
    stmt = select(Document).where(Document.is_deleted == False)

    if UserRole.ADMIN not in role_names:
        stmt = stmt.where(Document.is_public == True)

        if UserRole.PAID_USER not in role_names:
            # Free users: also filter paid content
            stmt = stmt.where(Document.requires_paid_access == False)

    result = await db.execute(stmt)
    return result.scalars().all()
```

---

## 5. Async Query Patterns

### Official Documentation
- **ORM Querying Guide**: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html
- **Relationship Loading**: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html

### 5.1 Basic Async Queries

```python
from sqlalchemy import select, and_, or_, func, exists
from sqlalchemy.orm import selectinload, joinedload

# Simple SELECT
async def get_user_by_id(user_id: UUID, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# Multiple conditions
async def search_users(username: str, email: str, db: AsyncSession):
    stmt = select(User).where(
        or_(
            User.username.ilike(f"%{username}%"),
            User.email.ilike(f"%{email}%")
        ),
        User.is_active == True
    )
    result = await db.execute(stmt)
    return result.scalars().all()

# Count queries
async def count_active_users(db: AsyncSession) -> int:
    stmt = select(func.count()).select_from(User).where(User.is_active == True)
    result = await db.execute(stmt)
    return result.scalar()

# Exists queries
async def user_exists(email: str, db: AsyncSession) -> bool:
    stmt = select(exists(select(User).where(User.email == email)))
    result = await db.execute(stmt)
    return result.scalar()
```

### 5.2 JOIN Queries with Role-Based Filtering

```python
async def get_documents_by_role_access(
    role_name: str,
    db: AsyncSession
) -> list[Document]:
    """
    Get documents accessible by specific role.
    Uses explicit JOIN with role configuration.
    """
    stmt = (
        select(Document)
        .join(Document.owner)
        .join(User.roles)
        .where(Role.name == role_name)
        .options(
            selectinload(Document.owner),
            selectinload(Document.owner).selectinload(User.roles)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_configurations_for_user_roles(
    user_id: UUID,
    db: AsyncSession
) -> list[Configuration]:
    """
    Get configurations accessible through user's roles.
    Demonstrates many-to-many JOIN with association object.
    """
    stmt = (
        select(Configuration)
        .join(RoleConfiguration, RoleConfiguration.configuration_id == Configuration.id)
        .join(Role, Role.id == RoleConfiguration.role_id)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(
            user_roles.c.user_id == user_id,
            RoleConfiguration.access_level >= 1
        )
        .options(selectinload(Configuration.roles))
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

### 5.3 Eager Loading Strategies (Critical for Async)

```python
from sqlalchemy.orm import selectinload, joinedload, subqueryload

# SELECTINLOAD - Best for one-to-many/many-to-many
async def get_users_with_roles_selectin(db: AsyncSession):
    """
    Uses 2 queries:
    1. SELECT users
    2. SELECT roles WHERE role.id IN (user_role_ids)

    Best for collections with many items.
    """
    stmt = select(User).options(selectinload(User.roles))
    result = await db.execute(stmt)
    return result.scalars().all()

# JOINEDLOAD - Best for many-to-one
async def get_documents_with_owners_joined(db: AsyncSession):
    """
    Uses 1 query with LEFT OUTER JOIN.
    Best for many-to-one (guaranteed single result).
    MUST call .unique() for one-to-many!
    """
    stmt = select(Document).options(
        joinedload(Document.owner, innerjoin=True)  # INNER JOIN if always exists
    )
    result = await db.execute(stmt)
    return result.scalars().unique().all()  # .unique() REQUIRED for collections

# CHAINED LOADING - Load nested relationships
async def get_users_full_hierarchy(db: AsyncSession):
    """
    Load users -> roles -> configurations in optimized way.
    Combines strategies for best performance.
    """
    stmt = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.configurations)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

# SUBQUERYLOAD - Alternative for large collections
async def get_users_with_many_docs(db: AsyncSession):
    """
    Uses subquery JOIN - good for very large collections.
    More queries but can be more efficient than selectin.
    """
    stmt = select(User).options(subqueryload(User.documents))
    result = await db.execute(stmt)
    return result.scalars().unique().all()
```

**Choosing Load Strategy:**

| Strategy | Use Case | Queries | Best For | Must Call .unique() |
|----------|----------|---------|----------|---------------------|
| `selectinload` | one-to-many, many-to-many | 1 + N per level | Most collections | No |
| `joinedload` | many-to-one | 1 (with JOIN) | Scalar relationships | Yes (for collections) |
| `subqueryload` | Very large collections | 1 + N per level | 1000+ items | Yes |

**Critical Async Rule:**
- **NEVER rely on lazy loading in async** - always use eager loading
- Lazy loading causes "greenlet" errors in async contexts
- Set `lazy="selectin"` on relationships OR use `.options()`

### 5.4 Filtering Through Relationships

```python
async def get_users_with_admin_role(db: AsyncSession):
    """
    Using .any() for filtering through relationship.
    Generates EXISTS subquery.
    """
    stmt = select(User).where(
        User.roles.any(Role.name == UserRole.ADMIN)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_users_without_roles(db: AsyncSession):
    """Negative relationship filtering with ~."""
    stmt = select(User).where(~User.roles.any())
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_documents_by_owner_role(role_name: str, db: AsyncSession):
    """
    Using .has() for many-to-one relationship filtering.
    """
    stmt = select(Document).where(
        Document.owner.has(
            User.roles.any(Role.name == role_name)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_active_paid_users_with_documents(db: AsyncSession):
    """
    Complex filtering with nested conditions.
    """
    stmt = (
        select(User)
        .where(
            and_(
                User.is_active == True,
                User.roles.any(Role.name == UserRole.PAID_USER),
                User.documents.any(Document.is_deleted == False)
            )
        )
        .options(
            selectinload(User.roles),
            selectinload(User.documents)
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()
```

### 5.5 INSERT, UPDATE, DELETE Operations

```python
# INSERT
async def create_user_with_roles(
    username: str,
    email: str,
    role_names: list[str],
    db: AsyncSession
) -> User:
    """Create user and assign roles in one transaction."""
    # Fetch roles
    stmt = select(Role).where(Role.name.in_(role_names))
    result = await db.execute(stmt)
    roles = result.scalars().all()

    # Create user with roles
    user = User(
        username=username,
        email=email,
        roles=roles  # Automatically populates association table
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)  # Refresh to get server-generated fields

    return user

# UPDATE
async def update_user_roles(
    user_id: UUID,
    new_role_names: list[str],
    db: AsyncSession
):
    """Replace user's roles."""
    # Fetch user with roles
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles))
    )
    result = await db.execute(stmt)
    user = result.scalar_one()

    # Fetch new roles
    role_stmt = select(Role).where(Role.name.in_(new_role_names))
    role_result = await db.execute(role_stmt)
    new_roles = role_result.scalars().all()

    # Replace roles (SQLAlchemy handles association table updates)
    user.roles = new_roles

    await db.commit()
    await db.refresh(user)

# DELETE
async def soft_delete_document(document_id: UUID, db: AsyncSession):
    """Soft delete - set flag instead of deleting row."""
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one()

    document.is_deleted = True

    await db.commit()

async def hard_delete_user(user_id: UUID, db: AsyncSession):
    """Hard delete - remove from database."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one()

    await db.delete(user)  # Cascades to user_roles if ondelete="CASCADE"
    await db.commit()
```

---

## 6. Alembic Configuration

### Official Documentation
- **Alembic Cookbook**: https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic
- **Async Migrations**: https://alembic.sqlalchemy.org/en/latest/cookbook.html

### 6.1 Initialize Alembic with Async Support

```bash
# Initialize with async template
alembic init -t async alembic

# Or for pyproject.toml projects
alembic init -t pyproject_async alembic
```

### 6.2 Configure alembic.ini

```ini
# alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .

# Database URL - can be overridden via env variable
sqlalchemy.url = postgresql+asyncpg://user:password@localhost:5432/dbname

# Timezone for migration timestamps
timezone = UTC

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 6.3 Configure env.py for Async Operations

```python
# alembic/env.py
import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import your models' Base for autogenerate
from app.database import Base  # Your declarative base
from app.models import User, Role, Document, Configuration  # Import ALL models

# Alembic Config object
config = context.config

# Override database URL from environment variable
if os.environ.get("DATABASE_URL"):
    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Setup Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode (generates SQL without DB connection).
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Detect column type changes
        compare_server_default=True,  # Detect default value changes
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """
    Inner function that runs migrations with a connection.
    Called by run_sync() from async context.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """
    Create async engine and run migrations in async context.
    """
    # Create async engine with NullPool
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Don't pool connections for migrations
    )

    async with connectable.connect() as connection:
        # Run migrations synchronously within async connection
        await connection.run_sync(do_run_migrations)

    # Dispose engine properly
    await connectable.dispose()

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode (connects to database).
    """
    # Check if we're running in programmatic mode (e.g., tests)
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        # Normal mode: create new engine and run async
        asyncio.run(run_async_migrations())
    else:
        # Programmatic mode: use provided connection
        do_run_migrations(connectable)

# Determine offline vs online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Key Configuration Points:**
- `pool.NullPool`: No connection pooling for migrations (safer)
- `compare_type=True`: Detect column type changes
- `compare_server_default=True`: Detect default value changes
- Import ALL models before `target_metadata = Base.metadata`

### 6.4 Creating and Running Migrations

```bash
# Create migration (autogenerate from models)
alembic revision --autogenerate -m "Add user roles and RBAC"

# Review generated migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history

# Rollback to specific revision
alembic downgrade <revision_id>

# Generate SQL without applying (offline mode)
alembic upgrade head --sql > migration.sql
```

### 6.5 Example Migration File

```python
# alembic/versions/xxxxx_add_rbac.py
"""Add user roles and RBAC

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2025-01-15 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = 'xxxxx'
down_revision: Union[str, None] = 'yyyyy'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_roles_name', 'roles', ['name'])

    # Create user_roles association table
    op.create_table(
        'user_roles',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Insert default roles
    op.execute("""
        INSERT INTO roles (id, name, description) VALUES
        (gen_random_uuid(), 'admin', 'Administrator with full access'),
        (gen_random_uuid(), 'paid_user', 'Paid user with premium features'),
        (gen_random_uuid(), 'free_user', 'Free user with basic features')
    """)

def downgrade() -> None:
    op.drop_table('user_roles')
    op.drop_index('ix_roles_name', table_name='roles')
    op.drop_table('roles')
```

---

## 7. Best Practices

### 7.1 Async Configuration

✅ **DO:**
- Always use `expire_on_commit=False` for async sessions
- Use `AsyncAttrs` mixin on Base for awaitable attributes
- Set `lazy="selectin"` on relationships or use explicit eager loading
- Use `NullPool` for migrations and testing
- Cache engine instance (singleton or `lru_cache`)

❌ **DON'T:**
- Never rely on lazy loading in async context
- Don't reuse sessions across requests
- Don't use synchronous drivers (psycopg2) with async engine
- Don't forget `await` before `session.execute()`

### 7.2 Relationship Loading

✅ **DO:**
- Use `selectinload()` for one-to-many and many-to-many
- Use `joinedload()` for many-to-one relationships
- Call `.unique()` after `joinedload()` for collections
- Chain loading options for nested relationships
- Set `innerjoin=True` on `joinedload()` for required relationships

❌ **DON'T:**
- Don't forget `.options()` for eager loading
- Don't mix `lazy="select"` (default) with async
- Don't access relationships without eager loading

### 7.3 Role-Based Access Control

✅ **DO:**
- Use event listeners (`do_orm_execute`) for global filtering
- Store user context in `ContextVar` for thread safety
- Provide bypass mechanism (`execution_options`)
- Use mixins for consistent access control fields
- Set `include_aliases=True` on `with_loader_criteria`

❌ **DON'T:**
- Don't hardcode role checks in every query
- Don't forget to set context before queries
- Don't apply filters to column/relationship loads
- Don't leak filtered data through relationships

### 7.4 Database Schema

✅ **DO:**
- Use UUID for primary keys in distributed systems
- Add indexes on foreign keys and frequently queried columns
- Use `ondelete="CASCADE"` for automatic cleanup
- Set `server_default` for timestamps and defaults
- Use `DateTime(timezone=True)` for timestamps

❌ **DON'T:**
- Don't forget `unique=True` constraints
- Don't use `Integer` auto-increment in multi-database setups
- Don't omit `nullable=False` when appropriate
- Don't forget indexes on columns used in WHERE clauses

### 7.5 Performance Optimization

✅ **DO:**
- Configure connection pooling (`pool_size`, `max_overflow`)
- Enable `pool_pre_ping` for connection health checks
- Use `pool_recycle` to prevent stale connections
- Batch INSERT operations when possible
- Use `returning()` to get inserted IDs in one query
- Profile queries with `echo=True` during development

❌ **DON'T:**
- Don't use `subqueryload()` unless necessary
- Don't fetch more data than needed
- Don't ignore N+1 query problems
- Don't forget to add indexes on JOIN columns

---

## 8. Common Gotchas

### 8.1 "Greenlet" Errors in Async

**Error:**
```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called
```

**Cause:** Accessing lazy-loaded relationship in async context

**Solutions:**
```python
# ✅ Solution 1: Use selectinload
stmt = select(User).options(selectinload(User.roles))

# ✅ Solution 2: Set lazy="selectin" on relationship
roles: Mapped[List["Role"]] = relationship(lazy="selectin")

# ✅ Solution 3: Use AsyncAttrs and await
user = await session.get(User, user_id)
roles = await user.awaitable_attrs.roles
```

### 8.2 Forgetting .unique() with joinedload()

**Error:** Duplicate results when using `joinedload()` on collections

**Solution:**
```python
# ❌ Wrong: Returns duplicate User objects
stmt = select(User).options(joinedload(User.roles))
users = result.scalars().all()  # Duplicates!

# ✅ Correct: Use .unique()
stmt = select(User).options(joinedload(User.roles))
users = result.scalars().unique().all()
```

### 8.3 expire_on_commit in Async

**Error:** Can't access attributes after commit in async

**Cause:** `expire_on_commit=True` (default) expires objects after commit

**Solution:**
```python
# ✅ Always set expire_on_commit=False for async
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False  # Required for async
)
```

### 8.4 Association Table vs Association Object

**When to Use Which:**

```python
# ✅ Association Table: No extra fields needed
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("role_id", ForeignKey("roles.id"))
)

# ✅ Association Object: Need timestamps, permissions, etc.
class UserRole(Base):
    __tablename__ = "user_roles"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    assigned_at: Mapped[datetime] = mapped_column(server_default=func.now())
    assigned_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
```

### 8.5 Session Lifecycle in FastAPI

**Wrong:**
```python
# ❌ Don't create session at module level
session = async_session_factory()

@app.get("/users")
async def get_users():
    return await session.execute(select(User))  # Shared across requests!
```

**Correct:**
```python
# ✅ Use dependency injection
async def get_db():
    async with async_session_factory() as session:
        yield session

@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### 8.6 UUID Generation: default vs default_factory

```python
# ❌ Wrong: Calls uuid4() once at class definition time
id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4())

# ✅ Correct: Passes function, called for each instance
id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

# ✅ Alternative: Use default_factory for dataclass pattern
class User(MappedAsDataclass, Base):
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)
```

### 8.7 Alembic Not Detecting Model Changes

**Cause:** Models not imported before `target_metadata = Base.metadata`

**Solution:**
```python
# alembic/env.py

# ✅ Import ALL models before target_metadata
from app.models import User, Role, Document, Configuration

# Now Base.metadata includes all tables
target_metadata = Base.metadata
```

### 8.8 Connection Pool Exhaustion

**Symptoms:** Application hangs, timeout errors

**Causes:**
- Sessions not closed properly
- Too many concurrent requests vs pool size
- Long-running transactions

**Solutions:**
```python
# ✅ Use context managers
async with async_session_factory() as session:
    # Session automatically closed

# ✅ Increase pool size
engine = create_async_engine(
    url,
    pool_size=20,  # Increase from default 5
    max_overflow=10
)

# ✅ Add timeout
engine = create_async_engine(
    url,
    pool_timeout=30  # Timeout after 30 seconds
)
```

---

## 9. Complete Example: FastAPI RBAC Application

### 9.1 Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── auth.py              # Authentication utilities
├── dependencies.py      # FastAPI dependencies
└── routers/
    ├── __init__.py
    ├── users.py
    └── documents.py
alembic/
├── env.py
└── versions/
requirements.txt
.env
```

### 9.2 database.py

```python
# app/database.py
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncAttrs
)
from sqlalchemy.orm import DeclarativeBase
from contextvars import ContextVar
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set False in production
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session factory
async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# Base class for models
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Context variable for current user roles
current_user_roles: ContextVar[set[str]] = ContextVar("current_user_roles", default=set())
```

### 9.3 models.py

```python
# app/models.py
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import Table, Column, String, Boolean, DateTime, ForeignKey, func, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, with_loader_criteria
from typing import List
from enum import Enum

from app.database import Base, current_user_roles

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    PAID_USER = "paid_user"
    FREE_USER = "free_user"

# Association table
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("assigned_at", DateTime(timezone=True), server_default=func.now()),
)

# Access control mixin
class HasAccessControl:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_paid_access: Mapped[bool] = mapped_column(Boolean, default=False)

# Models
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    roles: Mapped[List["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
        lazy="selectin"
    )
    documents: Mapped[List["Document"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255))

    users: Mapped[List["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin"
    )

class Document(HasAccessControl, Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str]
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="documents", lazy="selectin")

# Event listener for role-based filtering
@event.listens_for(Session, "do_orm_execute")
def apply_role_based_filtering(execute_state):
    if (
        execute_state.is_column_load
        or execute_state.is_relationship_load
        or execute_state.execution_options.get("include_filtered", False)
    ):
        return

    roles = current_user_roles.get()

    if UserRole.ADMIN in roles:
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                HasAccessControl,
                lambda cls: cls.is_deleted == False,
                include_aliases=True,
            )
        )
    elif UserRole.PAID_USER in roles:
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                HasAccessControl,
                lambda cls: (
                    (cls.is_deleted == False)
                    & (cls.is_public == True)
                ),
                include_aliases=True,
            )
        )
    else:
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                HasAccessControl,
                lambda cls: (
                    (cls.is_deleted == False)
                    & (cls.is_public == True)
                    & (cls.requires_paid_access == False)
                ),
                include_aliases=True,
            )
        )
```

### 9.4 dependencies.py

```python
# app/dependencies.py
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import async_session_factory, current_user_roles
from app.models import User

security = HTTPBearer()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Simplified - implement proper JWT decoding
    token = credentials.credentials
    user_id = decode_jwt(token)  # Your JWT logic

    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.roles))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user"
        )

    # Set roles in context for filtering
    role_names = {role.name for role in user.roles}
    current_user_roles.set(role_names)

    return user
```

### 9.5 main.py

```python
# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Document
from app.dependencies import get_current_user

app = FastAPI(title="RBAC Document API")

@app.get("/documents")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List documents - automatically filtered by role.
    """
    stmt = select(Document)
    result = await db.execute(stmt)
    documents = result.scalars().all()
    return documents

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 10. Quick Reference Cheat Sheet

### Engine & Session Setup
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine("postgresql+asyncpg://...", pool_size=20, pool_pre_ping=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

async with async_session_factory() as session:
    # Use session
    pass
```

### UUID Primary Keys
```python
from uuid import UUID, uuid4

id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
# OR
id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
```

### Many-to-Many
```python
assoc_table = Table("assoc", Base.metadata,
    Column("left_id", ForeignKey("left.id"), primary_key=True),
    Column("right_id", ForeignKey("right.id"), primary_key=True)
)

class Left(Base):
    rights: Mapped[List["Right"]] = relationship(secondary=assoc_table, lazy="selectin")
```

### Async Queries
```python
# SELECT
stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))
result = await session.execute(stmt)
user = result.scalar_one_or_none()

# INSERT
user = User(username="john")
session.add(user)
await session.commit()
await session.refresh(user)

# UPDATE
user.username = "jane"
await session.commit()

# DELETE
await session.delete(user)
await session.commit()
```

### Role-Based Filtering
```python
from sqlalchemy.orm import with_loader_criteria

@event.listens_for(Session, "do_orm_execute")
def filter_by_role(execute_state):
    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(Model, lambda cls: cls.is_public == True, include_aliases=True)
    )
```

### Alembic Commands
```bash
alembic init -t async alembic
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
```

---

## 11. Additional Resources

### Official Documentation
- **SQLAlchemy 2.0 Docs**: https://docs.sqlalchemy.org/en/20/
- **AsyncIO Extension**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **ORM Query Guide**: https://docs.sqlalchemy.org/en/20/orm/queryguide/index.html
- **Relationship Loading**: https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html
- **Alembic Docs**: https://alembic.sqlalchemy.org/en/latest/

### Tutorials & Articles
- **TestDriven.io FastAPI SQLModel Guide**: https://testdriven.io/blog/fastapi-sqlmodel/
- **Berk Karaal FastAPI Setup**: https://berkkaraal.com/blog/2024/09/19/setup-fastapi-project-with-async-sqlalchemy-2-alembic-postgresql-and-docker/
- **Medium - Setting up FastAPI with Async SQLAlchemy**: https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308

### GitHub Examples
- **seapagan/fastapi_async_sqlalchemy2_example**: https://github.com/seapagan/fastapi_async_sqlalchemy2_example

---

**Document Version:** 1.0
**Last Updated:** 2025-01-17
**SQLAlchemy Version:** 2.0+
**FastAPI Compatibility:** 0.115.0+
**Python Version:** 3.10+
