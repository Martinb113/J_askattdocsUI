"""
Admin API endpoints for managing users, roles, domains, and configurations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.api.deps import get_db, get_current_user, require_admin
from app.schemas.admin import (
    RoleResponse,
    RoleCreateRequest,
    DomainCreateRequest,
    ConfigurationCreateRequest,
    UserRoleAssignment,
    UsageStatsResponse,
    FetchConfigurationsRequest,
    FetchConfigurationsResponse,
)
from app.schemas.auth import UserResponse
from app.schemas.chat import ConfigurationResponse, DomainResponse
from app.models.user import User, Role
from app.models.domain import Domain, Configuration
from app.models.conversation import Conversation, Message
from app.models.feedback import TokenUsageLog
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from app.services.askdocs_config import fetch_configurations_by_domain, fetch_configurations_by_domain_mock
from app.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users (Admin only).

    **Query Parameters:**
    - `limit`: Max users to return (default 100)
    - `offset`: Pagination offset (default 0)

    **Returns:**
    - List of users with roles
    """
    stmt = (
        select(User)
        .options(selectinload(User.roles))
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    users = result.scalars().all()

    return [
        UserResponse(
            id=user.id,
            attid=user.attid,
            email=user.email,
            full_name=user.display_name,
            is_active=user.is_active,
            created_at=user.created_at,
            roles=[role.name for role in user.roles]
        )
        for user in users
    ]


@router.post("/users/{user_id}/roles", response_model=UserResponse)
async def assign_user_roles(
    user_id: UUID,
    request: UserRoleAssignment,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign roles to a user (Admin only).

    **Request Body:**
    - `role_ids`: List of role UUIDs to assign

    **Returns:**
    - Updated user with new roles
    """
    # Get user
    stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Get roles
    stmt = select(Role).where(Role.id.in_(request.role_ids))
    result = await db.execute(stmt)
    roles = result.scalars().all()

    if len(roles) != len(request.role_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Some roles not found")

    # Replace user roles
    user.roles = roles

    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        attid=user.attid,
        email=user.email,
        full_name=user.display_name,
        is_active=user.is_active,
        created_at=user.created_at,
        roles=[role.name for role in user.roles]
    )


@router.get("/roles", response_model=list[RoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all roles (Admin only).

    **Returns:**
    - List of all roles
    """
    stmt = select(Role)
    result = await db.execute(stmt)
    roles = result.scalars().all()

    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            created_at=role.created_at
        )
        for role in roles
    ]


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    request: RoleCreateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new role (Admin only).

    **Request Body:**
    - `name`: Role name (unique, uppercase recommended)
    - `description`: Optional description

    **Returns:**
    - Created role
    """
    # Check if role already exists
    stmt = select(Role).where(Role.name == request.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Role '{request.name}' already exists"
        )

    role = Role(
        name=request.name,
        description=request.description
    )

    db.add(role)
    await db.commit()
    await db.refresh(role)

    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        created_at=role.created_at
    )


@router.get("/domains", response_model=list[DomainResponse])
async def list_domains(
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all AskDocs domains (Admin only).

    **Returns:**
    - List of all domains
    """
    stmt = select(Domain)
    result = await db.execute(stmt)
    domains = result.scalars().all()

    return [
        DomainResponse(
            id=domain.id,
            domain_key=domain.domain_key,
            display_name=domain.display_name,
            description=domain.description
        )
        for domain in domains
    ]


@router.post("/domains", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def create_domain(
    request: DomainCreateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new AskDocs domain (Admin only).

    **Request Body:**
    - `domain_key`: Domain identifier (e.g., "att_support")
    - `display_name`: Human-readable name
    - `description`: Optional description

    **Returns:**
    - Created domain
    """
    # Check if domain_key already exists
    stmt = select(Domain).where(Domain.domain_key == request.domain_key)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Domain key '{request.domain_key}' already exists"
        )

    domain = Domain(
        domain_key=request.domain_key,
        display_name=request.display_name,
        description=request.description
    )

    db.add(domain)
    await db.commit()
    await db.refresh(domain)

    return DomainResponse(
        id=domain.id,
        domain_key=domain.domain_key,
        display_name=domain.display_name,
        description=domain.description
    )


@router.get("/configurations", response_model=list[ConfigurationResponse])
async def list_all_configurations(
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List ALL configurations (Admin only, bypasses role filtering).

    **Returns:**
    - List of all configurations with domains
    """
    stmt = (
        select(Configuration)
        .options(selectinload(Configuration.domain))
    )

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


@router.post("/configurations", response_model=ConfigurationResponse, status_code=status.HTTP_201_CREATED)
async def create_configuration(
    request: ConfigurationCreateRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new AskDocs configuration (Admin only).

    **Request Body:**
    - `domain_id`: Domain UUID
    - `config_key`: Configuration identifier
    - `display_name`: Human-readable name
    - `description`: Optional description
    - `environment`: "stage" or "production"
    - `is_active`: Boolean (default true)
    - `role_ids`: List of role UUIDs with access

    **Returns:**
    - Created configuration with assigned roles
    """
    # Verify domain exists
    stmt = select(Domain).where(Domain.id == request.domain_id)
    result = await db.execute(stmt)
    domain = result.scalar_one_or_none()

    if not domain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Domain not found")

    # Check if config_key already exists in this domain
    stmt = select(Configuration).where(
        Configuration.domain_id == request.domain_id,
        Configuration.config_key == request.config_key
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Configuration '{request.config_key}' already exists in this domain"
        )

    # Get roles
    stmt = select(Role).where(Role.id.in_(request.role_ids))
    result = await db.execute(stmt)
    roles = result.scalars().all()

    if len(roles) != len(request.role_ids):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Some roles not found")

    # Create configuration
    config = Configuration(
        domain_id=request.domain_id,
        config_key=request.config_key,
        display_name=request.display_name,
        description=request.description,
        environment=request.environment,
        is_active=request.is_active
    )

    # Assign roles
    config.roles = roles

    db.add(config)
    await db.commit()
    await db.refresh(config)

    # Load domain for response
    stmt = select(Configuration).where(Configuration.id == config.id).options(selectinload(Configuration.domain))
    result = await db.execute(stmt)
    config = result.scalar_one()

    return ConfigurationResponse(
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


@router.get("/stats/usage", response_model=UsageStatsResponse)
async def get_usage_statistics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get token usage statistics for the specified period (Admin only).

    **Query Parameters:**
    - `days`: Number of days to look back (default 30)

    **Returns:**
    - Aggregated usage statistics
    """
    period_start = datetime.utcnow() - timedelta(days=days)

    # Count conversations
    conv_stmt = select(func.count()).select_from(Conversation).where(
        Conversation.created_at >= period_start
    )
    conv_result = await db.execute(conv_stmt)
    total_conversations = conv_result.scalar()

    # Count messages
    msg_stmt = select(func.count()).select_from(Message).where(
        Message.created_at >= period_start
    )
    msg_result = await db.execute(msg_stmt)
    total_messages = msg_result.scalar()

    # Sum token usage from messages
    token_stmt = select(func.sum(Message.token_usage)).where(
        Message.created_at >= period_start,
        Message.token_usage.isnot(None)
    )
    token_result = await db.execute(token_stmt)

    # Calculate token totals (this is a simplified version)
    # In production, you'd parse the JSONB token_usage field
    total_tokens = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0

    return UsageStatsResponse(
        total_conversations=total_conversations or 0,
        total_messages=total_messages or 0,
        total_tokens=total_tokens,
        total_prompt_tokens=total_prompt_tokens,
        total_completion_tokens=total_completion_tokens,
        period_start=period_start,
        period_end=datetime.utcnow()
    )


@router.post("/configurations/fetch-by-domain", response_model=FetchConfigurationsResponse)
async def fetch_configurations_for_domain(
    request: FetchConfigurationsRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_admin())
):
    """
    Fetch configurations for a domain from external AskDocs API (Admin only).

    This endpoint proxies requests to the external AskDocs configuration API
    to retrieve available configurations for a specific domain.

    **Request Body:**
    - `domain`: Domain name to fetch configurations for
    - `log_as_userid`: User ID for logging purposes in external API
    - `environment`: "stage" or "production" (default: "production")

    **Returns:**
    - `data`: JSON string containing configuration data from external API

    **Example:**
    ```bash
    curl -X POST http://localhost:8000/api/v1/admin/configurations/fetch-by-domain \\
      -H "Authorization: Bearer <admin_token>" \\
      -H "Content-Type: application/json" \\
      -d '{
        "domain": "att_support",
        "log_as_userid": "admin",
        "environment": "production"
      }'
    ```

    **Note:** When `USE_MOCK_ASKDOCS=true` in .env, this will return mock data.
    """
    try:
        # Use mock or real implementation based on settings
        if settings.USE_MOCK_ASKDOCS:
            config_data = await fetch_configurations_by_domain_mock(
                domain_name=request.domain,
                log_as_userid=request.log_as_userid,
                environment=request.environment
            )
        else:
            config_data = await fetch_configurations_by_domain(
                domain_name=request.domain,
                log_as_userid=request.log_as_userid,
                environment=request.environment
            )

        return FetchConfigurationsResponse(data=config_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch configurations: {str(e)}"
        )
