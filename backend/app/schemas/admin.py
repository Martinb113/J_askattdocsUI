"""
Pydantic schemas for admin endpoints.
"""
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class RoleResponse(BaseModel):
    """Role response."""
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RoleCreateRequest(BaseModel):
    """Create role request."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)


class DomainCreateRequest(BaseModel):
    """Create domain request."""
    domain_key: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)


class ConfigurationCreateRequest(BaseModel):
    """Create configuration request."""
    domain_id: UUID
    config_key: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    environment: str = Field(default="production", pattern="^(stage|production)$")
    is_active: bool = Field(default=True)
    role_ids: list[UUID] = Field(default_factory=list, description="Roles with access to this config")


class UserRoleAssignment(BaseModel):
    """Assign/remove roles for a user."""
    user_id: UUID
    role_ids: list[UUID] = Field(..., description="List of role IDs to assign")


class UsageStatsResponse(BaseModel):
    """Token usage statistics."""
    total_conversations: int
    total_messages: int
    total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    period_start: datetime
    period_end: datetime


class FetchConfigurationsRequest(BaseModel):
    """Request to fetch configurations for a domain from external API."""
    domain: str = Field(..., min_length=1, max_length=100, description="Domain name to fetch configurations for")
    log_as_userid: str = Field(..., min_length=1, max_length=100, description="User ID for logging purposes")
    environment: str = Field(default="production", pattern="^(stage|production)$", description="Environment: stage or production")


class FetchConfigurationsResponse(BaseModel):
    """Response from fetching domain configurations."""
    data: str = Field(..., description="Configuration data as JSON string from external API")
