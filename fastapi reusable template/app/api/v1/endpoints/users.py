from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_roles
from app.models.user import User, UserRole
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@router.get("/admin-check", response_model=UserResponse)
async def admin_check(
    user: Annotated[User, Depends(require_roles(UserRole.ADMIN))],
) -> User:
    return user
