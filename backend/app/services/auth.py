"""
Authentication service with business logic for user signup and login.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.user import User, Role
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import AuthenticationError, ValidationError


async def create_user(
    db: AsyncSession,
    attid: str,
    email: str,
    password: str,
    full_name: str
) -> User:
    """
    Create a new user account.

    Args:
        db: Database session
        attid: AT&T ID (unique identifier)
        email: User email address
        password: Plain text password (will be hashed)
        full_name: User's full name

    Returns:
        User: Newly created user with default USER role

    Raises:
        ValidationError: If attid or email already exists
    """
    # Check if attid already exists
    stmt = select(User).where(User.attid == attid)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValidationError(f"AT&T ID '{attid}' is already registered")

    # Check if email already exists
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise ValidationError(f"Email '{email}' is already registered")

    # Get the default USER role
    stmt = select(Role).where(Role.name == "USER")
    result = await db.execute(stmt)
    user_role = result.scalar_one_or_none()

    if not user_role:
        # If USER role doesn't exist, create it
        user_role = Role(
            name="USER",
            description="Basic user with access to general chat"
        )
        db.add(user_role)
        await db.flush()  # Get the role ID

    # Hash the password
    password_hash = get_password_hash(password)

    # Create new user
    new_user = User(
        attid=attid,
        email=email,
        password_hash=password_hash,
        display_name=full_name,
        is_active=True
    )

    # Assign default USER role
    new_user.roles.append(user_role)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def authenticate_user(
    db: AsyncSession,
    attid: str,
    password: str
) -> Optional[User]:
    """
    Authenticate user by attid and password.

    Args:
        db: Database session
        attid: AT&T ID
        password: Plain text password

    Returns:
        User: Authenticated user if credentials are valid, None otherwise
    """
    # Retrieve user by attid
    stmt = select(User).where(User.attid == attid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Verify password
    if not verify_password(password, user.password_hash):
        return None

    # Check if user is active
    if not user.is_active:
        return None

    return user


async def login_user(
    db: AsyncSession,
    attid: str,
    password: str
) -> tuple[str, User]:
    """
    Login user and generate JWT access token.

    Args:
        db: Database session
        attid: AT&T ID
        password: Plain text password

    Returns:
        tuple: (access_token, user)

    Raises:
        AuthenticationError: If credentials are invalid
    """
    # Authenticate user
    user = await authenticate_user(db, attid, password)

    if not user:
        raise AuthenticationError("Invalid AT&T ID or password")

    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return access_token, user


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """
    Retrieve user by ID.

    Args:
        db: Database session
        user_id: User UUID as string

    Returns:
        User: User if found, None otherwise
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_attid(db: AsyncSession, attid: str) -> Optional[User]:
    """
    Retrieve user by AT&T ID.

    Args:
        db: Database session
        attid: AT&T ID

    Returns:
        User: User if found, None otherwise
    """
    stmt = select(User).where(User.attid == attid)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
