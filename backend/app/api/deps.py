"""
FastAPI dependencies for database sessions, authentication, and authorization.
"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.models import current_user_roles  # ContextVar for role-based filtering


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session that will be automatically closed
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency that validates JWT token and returns current user.

    This extracts the Bearer token from the Authorization header,
    validates it, and retrieves the corresponding user from the database.

    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session

    Returns:
        User: The authenticated user

    Raises:
        AuthenticationError: If token is invalid or user not found

    Usage:
        @app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise AuthenticationError("Invalid token payload")

    except JWTError as e:
        raise AuthenticationError(f"Token validation failed: {str(e)}")

    # Retrieve user from database
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    return user


async def get_current_user_with_context(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency that validates JWT token, returns current user, AND sets role context.

    This is CRITICAL for role-based access control. It sets the current_user_roles
    ContextVar which is used by the SQLAlchemy event listener to automatically
    filter queries based on user roles.

    Use this dependency instead of get_current_user when you need role-based filtering
    (e.g., for Configuration queries in AskDocs endpoints).

    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session

    Returns:
        User: The authenticated user (with roles loaded)

    Raises:
        AuthenticationError: If token is invalid or user not found

    Usage:
        @app.get("/configurations")
        async def list_configs(current_user: User = Depends(get_current_user_with_context)):
            # Configuration queries will be automatically filtered by user's roles
            ...
    """
    # Get the current user (same as get_current_user)
    user = await get_current_user(credentials, db)

    # Extract role names from user.roles (relationship is lazy="selectin" so already loaded)
    role_names = [role.name for role in user.roles]

    # Set the ContextVar for role-based filtering
    # This will be used by the SQLAlchemy event listener in app.models.__init__.py
    current_user_roles.set(role_names)

    return user


def require_role(*required_roles: str):
    """
    Dependency factory that requires user to have at least one of the specified roles.

    Args:
        *required_roles: One or more role names (e.g., "ADMIN", "MANAGER")

    Returns:
        Dependency function that validates user roles

    Raises:
        HTTPException: 403 Forbidden if user lacks required roles

    Usage:
        @app.post("/admin/users")
        async def create_user(
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_role("ADMIN"))
        ):
            # Only users with ADMIN role can access this endpoint
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> None:
        user_roles = {role.name for role in current_user.roles}

        # Check if user has any of the required roles
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role(s): {', '.join(required_roles)}"
            )

    return role_checker


def require_admin():
    """
    Convenience dependency that requires ADMIN role.

    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: UUID,
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_admin())
        ):
            ...
    """
    return require_role("ADMIN")
