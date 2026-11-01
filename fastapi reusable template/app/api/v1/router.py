from fastapi import APIRouter

from app.api.v1.auth.auth_router import router as auth_router
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
