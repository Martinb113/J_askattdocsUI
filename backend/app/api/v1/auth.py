"""
Authentication API endpoints for user signup, login, and profile.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.schemas.auth import SignupRequest, LoginRequest, LoginResponse, UserResponse
from app.services.auth import create_user, login_user
from app.models.user import User
from app.core.exceptions import ValidationError, AuthenticationError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.

    Creates a new user with the provided credentials and assigns the default USER role.

    **Request Body:**
    - `attid`: AT&T ID (unique identifier)
    - `email`: Email address (must be unique)
    - `password`: Password (min 8 chars, must include uppercase, lowercase, digit)
    - `full_name`: User's full name

    **Returns:**
    - User profile with assigned roles

    **Errors:**
    - `422`: Password doesn't meet complexity requirements
    - `422`: AT&T ID or email already registered
    """
    try:
        user = await create_user(
            db=db,
            attid=request.attid,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )

        # Convert to response model
        return UserResponse(
            id=user.id,
            attid=user.attid,
            email=user.email,
            full_name=user.display_name,
            is_active=user.is_active,
            created_at=user.created_at,
            roles=[role.name for role in user.roles]
        )

    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with AT&T ID and password.

    Authenticates user credentials and returns a JWT access token.

    **Request Body:**
    - `attid`: AT&T ID
    - `password`: Password

    **Returns:**
    - `access_token`: JWT token for authenticated requests
    - `token_type`: "bearer"
    - `user`: User profile with roles

    **Errors:**
    - `401`: Invalid credentials or inactive account

    **Example:**
    ```bash
    curl -X POST http://localhost:8000/api/v1/auth/login \\
      -H "Content-Type: application/json" \\
      -d '{"attid": "ab1234", "password": "SecurePass123"}'
    ```

    Then use the token in subsequent requests:
    ```bash
    curl -X GET http://localhost:8000/api/v1/auth/me \\
      -H "Authorization: Bearer <access_token>"
    ```
    """
    try:
        access_token, user = await login_user(
            db=db,
            attid=request.attid,
            password=request.password
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                attid=user.attid,
                email=user.email,
                full_name=user.display_name,
                is_active=user.is_active,
                created_at=user.created_at,
                roles=[role.name for role in user.roles]
            )
        )

    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.

    Requires valid JWT token in Authorization header.

    **Returns:**
    - User profile with roles

    **Errors:**
    - `401`: Invalid or missing token

    **Example:**
    ```bash
    curl -X GET http://localhost:8000/api/v1/auth/me \\
      -H "Authorization: Bearer <your_token>"
    ```
    """
    return UserResponse(
        id=current_user.id,
        attid=current_user.attid,
        email=current_user.email,
        full_name=current_user.display_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        roles=[role.name for role in current_user.roles]
    )
