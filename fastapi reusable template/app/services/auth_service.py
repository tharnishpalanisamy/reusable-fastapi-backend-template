from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.exceptions.auth import InvalidCredentialsException, InvalidRefreshTokenException
from app.exceptions.user import EmailAlreadyExistsException
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)

    async def _issue_tokens(self, user: User) -> dict[str, str]:
        raw = create_refresh_token()
        record = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
        await self.refresh_tokens.create(record)
        return {"access_token": create_access_token(user.id), "refresh_token": raw, "token_type": "bearer"}

    async def signup(self, payload: UserCreate) -> tuple[User, dict[str, str]]:
        email = str(payload.email).lower()
        if await self.users.exists_by_email(email):
            raise EmailAlreadyExistsException()
        user = User(
            username=payload.username,
            email=email,
            password_hash=hash_password(payload.password),
            role=UserRole.USER,
        )
        try:
            await self.users.create(user)
            tokens = await self._issue_tokens(user)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return user, tokens

    async def login(self, email: str, password: str) -> tuple[User, dict[str, str]]:
        user = await self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash) or not user.is_active:
            raise InvalidCredentialsException()
        tokens = await self._issue_tokens(user)
        await self.session.commit()
        return user, tokens

    async def rotate_refresh_token(self, raw_token: str) -> dict[str, str]:
        now = datetime.now(UTC)
        record = await self.refresh_tokens.get_by_hash_for_update(hash_refresh_token(raw_token))
        if record is None:
            await self.session.rollback()
            raise InvalidRefreshTokenException()
        if record.revoked_at is not None:
            # Reuse detection must commit even though the request is rejected.
            await self.refresh_tokens.revoke_active_for_user(record.user_id, now)
            await self.session.commit()
            raise InvalidRefreshTokenException()

        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        user = await self.users.get_by_id(record.user_id)
        if expires_at <= now or user is None or not user.is_active:
            await self.session.rollback()
            raise InvalidRefreshTokenException()

        new_raw = create_refresh_token()
        replacement = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(new_raw),
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        )
        await self.refresh_tokens.create(replacement)
        await self.refresh_tokens.revoke(record, now, replacement.id)
        result = {
            "access_token": create_access_token(user.id),
            "refresh_token": new_raw,
            "token_type": "bearer",
        }
        await self.session.commit()
        return result

    async def logout(self, raw_token: str) -> None:
        record = await self.refresh_tokens.get_by_hash_for_update(hash_refresh_token(raw_token))
        if record and record.revoked_at is None:
            await self.refresh_tokens.revoke(record, datetime.now(UTC))
        await self.session.commit()
