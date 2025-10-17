"""
Models package initialization.
Imports all models and sets up global role-based filtering via SQLAlchemy event listeners.
"""
from app.database import Base
from app.models.user import User, Role, user_roles
from app.models.domain import Domain, Configuration, role_configuration_access
from app.models.conversation import Conversation, Message
from app.models.feedback import Feedback, TokenUsageLog

# Import for event listener
from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria
from contextvars import ContextVar

# Thread-safe context variable for current user roles
# This is set by the get_current_user_with_context dependency in FastAPI
current_user_roles: ContextVar[set[str]] = ContextVar("current_user_roles", default=set())


@event.listens_for(Session, "do_orm_execute")
def apply_role_based_filtering(execute_state):
    """
    Automatically filter queries based on current user's roles.
    Applies to Configuration model based on role_configuration_access.

    This event listener is called for EVERY query, providing global role-based filtering.
    ADMIN users bypass filtering. Other users only see configurations their roles have access to.

    CRITICAL: This implements the PRP requirement for role-based filtering at database query level.
    """
    # Skip filtering for relationship/column loads
    if execute_state.is_column_load or execute_state.is_relationship_load:
        return

    # Get current user's roles from context
    roles = current_user_roles.get()

    # Skip filtering if no roles set or user is ADMIN
    if not roles or "ADMIN" in roles:
        return

    # Apply filtering for Configuration model
    # Users only see configurations that their role(s) have access to
    execute_state.statement = execute_state.statement.options(
        with_loader_criteria(
            Configuration,
            lambda cls: cls.roles.any(Role.name.in_(roles)),
            include_aliases=True
        )
    )


# Export all models for easy import
__all__ = [
    "Base",
    "User",
    "Role",
    "user_roles",
    "Domain",
    "Configuration",
    "role_configuration_access",
    "Conversation",
    "Message",
    "Feedback",
    "TokenUsageLog",
    "current_user_roles",
]
