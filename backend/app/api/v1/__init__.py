"""
API v1 router that combines all endpoint routers.
"""
from fastapi import APIRouter
from app.api.v1 import auth, chat, admin

# Create v1 API router
api_router = APIRouter(prefix="/v1")

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(admin.router)
