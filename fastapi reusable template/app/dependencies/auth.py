from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database.session import get_db
from app.exceptions.auth import InvalidAccessTokenException
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: DbSession,
) -> User:
    if credentials is None:
        raise InvalidAccessTokenException()
    payload = decode_access_token(credentials.credentials)
    user = await UserRepository(session).get_by_id(UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise InvalidAccessTokenException()
    return user
