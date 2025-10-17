"""
Pydantic schemas for API validation and serialization.
"""
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    LoginResponse,
    UserResponse,
    TokenPayload,
)
from app.schemas.chat import (
    ChatRequest,
    MessageResponse,
    ConversationResponse,
    ConversationListItem,
    FeedbackRequest,
    FeedbackResponse,
    ConfigurationResponse,
    DomainResponse,
)
from app.schemas.admin import (
    RoleResponse,
    RoleCreateRequest,
    DomainCreateRequest,
    ConfigurationCreateRequest,
    UserRoleAssignment,
    UsageStatsResponse,
)

__all__ = [
    # Auth
    "SignupRequest",
    "LoginRequest",
    "LoginResponse",
    "UserResponse",
    "TokenPayload",
    # Chat
    "ChatRequest",
    "MessageResponse",
    "ConversationResponse",
    "ConversationListItem",
    "FeedbackRequest",
    "FeedbackResponse",
    "ConfigurationResponse",
    "DomainResponse",
    # Admin
    "RoleResponse",
    "RoleCreateRequest",
    "DomainCreateRequest",
    "ConfigurationCreateRequest",
    "UserRoleAssignment",
    "UsageStatsResponse",
]
