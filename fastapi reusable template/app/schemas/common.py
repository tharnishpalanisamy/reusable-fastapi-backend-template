from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: None = None
    errors: dict | list | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)


def pagination_offset(page: int, page_size: int) -> int:
    if page < 1 or not 1 <= page_size <= 100:
        raise ValueError("page must be >= 1 and page_size must be between 1 and 100")
    return (page - 1) * page_size
