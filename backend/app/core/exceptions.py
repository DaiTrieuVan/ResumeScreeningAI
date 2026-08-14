from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict

class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
    invalid_params: Optional[Any] = None

class AppException(Exception):
    def __init__(
        self,
        title: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "",
        type_uri: str = "about:blank",
        invalid_params: Optional[Any] = None
    ):
        self.title = title
        self.status_code = status_code
        self.detail = detail
        self.type_uri = type_uri
        self.invalid_params = invalid_params
        super().__init__(detail or title)

class ResourceNotFoundException(AppException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            title="Resource Not Found",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' was not found.",
            type_uri="https://api.resumescreening.ai/errors/not-found"
        )

class ParsingException(AppException):
    def __init__(self, filename: str, reason: str):
        super().__init__(
            title="Document Parsing Error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse resume document '{filename}': {reason}",
            type_uri="https://api.resumescreening.ai/errors/parsing-failed"
        )

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    problem = ProblemDetails(
        type=exc.type_uri,
        title=exc.title,
        status=exc.status_code,
        detail=exc.detail,
        instance=request.url.path,
        invalid_params=exc.invalid_params
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True),
        headers={"Content-Type": "application/problem+json"}
    )
