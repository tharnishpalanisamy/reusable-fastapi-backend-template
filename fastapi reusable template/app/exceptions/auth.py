from app.exceptions.base import AppException


class InvalidCredentialsException(AppException):
    status_code = 401
    message = "Invalid email or password"


class InvalidAccessTokenException(AppException):
    status_code = 401
    message = "Invalid or expired access token"


class InvalidRefreshTokenException(AppException):
    status_code = 401
    message = "Invalid or expired refresh token"


class InsufficientPermissionsException(AppException):
    status_code = 403
    message = "Insufficient permissions"
