from app.exceptions.base import AppException


class UserNotFoundException(AppException):
    status_code = 404
    message = "User not found"


class EmailAlreadyExistsException(AppException):
    status_code = 409
    message = "Email already registered"
