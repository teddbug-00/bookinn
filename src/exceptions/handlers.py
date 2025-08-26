from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from src.exceptions.base import AppError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic's validation errors to provide a cleaner,
    more friendly response format.
    """
    error_messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error.get("loc", []) if loc != "body")
        message = error.get("msg", "An unknown validation error occurred.")
        error_messages.append(f"Error in field '{field}': {message}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Your request could not be processed due to validation errors.", "errors": error_messages},
    )


async def app_exception_handler(request: Request, exc: AppError):
    """Global handler to catch all AppError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


exception_handlers = [
    (RequestValidationError, validation_exception_handler),
    (AppError, app_exception_handler)
]
