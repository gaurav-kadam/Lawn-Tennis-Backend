from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.exceptions.base import AppException
from app.utils.logger import logger


def build_error_response(
    status_code: int,
    message: str,
    details=None
):
    """
    Standard Error Response Builder
    """

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "status": status_code,
            "message": message,
            "data": None,
            "details": details
        }
    )


async def app_exception_handler(
    request: Request,
    exc: AppException
):
    """
    Handles all Custom Exceptions
    """

    logger.warning(
        f"{request.method} {request.url.path} | {exc.message}"
    )

    return build_error_response(
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """
    Handles Pydantic Validation Errors
    """

    logger.warning(
        f"Validation Error | {request.method} {request.url.path}"
    )

    errors = []

    for error in exc.errors():
        # Never echo the raw submitted value back (e.g. a mistyped password) -
        # field + message is enough for the client to fix the form.
        errors.append({
            "field": ".".join(
                map(str, error["loc"])
            ),
            "message": error["msg"]
        })

    return build_error_response(
        status_code=422,
        message="Validation Error",
        details=errors
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    """
    Handles FastAPI/Starlette HTTP Exceptions (e.g. from HTTPBearer's
    "Not authenticated" when the Authorization header is missing entirely)
    """

    logger.warning(
        f"HTTP Exception | {request.method} {request.url.path} | {exc.detail}"
    )

    return build_error_response(
        status_code=exc.status_code,
        message=str(exc.detail)
    )


async def global_exception_handler(
    request: Request,
    exc: Exception
):
    """
    Handles Unexpected Exceptions - full traceback goes to the log only,
    the client never sees internal details (no SQL, no file paths, no
    stack trace).
    """

    logger.exception(
        f"Unhandled Exception | {request.method} {request.url.path}"
    )

    return build_error_response(
        status_code=500,
        message="Internal Server Error"
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
