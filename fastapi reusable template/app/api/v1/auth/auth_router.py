from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import DbSession, get_current_user
from app.models.user import User
from app.schemas.auth import AuthResponse, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, session: DbSession) -> AuthResponse:
    user, tokens = await AuthService(session).signup(payload)
    return AuthResponse(user=user, tokens=TokenResponse(**tokens))


@router.post("/login", response_model=AuthResponse)
async def login(payload: UserLogin, session: DbSession) -> AuthResponse:
    user, tokens = await AuthService(session).login(str(payload.email), payload.password)
    return AuthResponse(user=user, tokens=TokenResponse(**tokens))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest, session: DbSession) -> TokenResponse:
    return TokenResponse(**await AuthService(session).rotate_refresh_token(payload.refresh_token))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshTokenRequest, session: DbSession) -> None:
    await AuthService(session).logout(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user
