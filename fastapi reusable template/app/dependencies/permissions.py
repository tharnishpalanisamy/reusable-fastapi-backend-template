from collections.abc import Callable

from fastapi import Depends

from app.dependencies.auth import get_current_user
from app.exceptions.auth import InsufficientPermissionsException
from app.models.user import User, UserRole


def require_roles(*allowed_roles: UserRole) -> Callable:
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise InsufficientPermissionsException()
        return user

    return dependency
