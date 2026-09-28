from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.responses.response_builder import error_response
from app.exceptions.base import AppException
from app.utils.logger import logger


def build_error_response(status_code: int, message: str, details=None, headers=None):
    errors = details if details is None or isinstance(details, list) else [details]
    response = error_response(message=message, errors=errors, status_code=status_code)
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(mode="json"),
        headers=headers,
    )


async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"{request.method} {request.url.path} | {exc.message}")

    return build_error_response(
        status_code=exc.status_code, message=exc.message, details=exc.details
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation Error | {request.method} {request.url.path}")

    errors = []

    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(map(str, error["loc"])),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return build_error_response(
        status_code=422, message="Validation Error", details=errors
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        f"HTTP Exception | {request.method} {request.url.path} | {exc.detail}"
    )

    return build_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        headers=exc.headers,
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Exception | {request.method} {request.url.path}")

    return build_error_response(status_code=500, message="Internal Server Error")


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
