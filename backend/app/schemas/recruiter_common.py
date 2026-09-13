from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class ProblemDetail(BaseModel):
    code: str
    message: str
    field_errors: dict[str, str] = Field(default_factory=dict)
    request_id: str | None = None


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total: int = Field(ge=0)
    facets: dict[str, Any] = Field(default_factory=dict)
