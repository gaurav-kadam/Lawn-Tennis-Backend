from fastapi.encoders import jsonable_encoder

from app.responses.response_model import ApiResponse


def success_response(message: str, data=None, status_code: int = 200):
    return ApiResponse(
        success=True,
        message=message,
        status_code=status_code,
        data=jsonable_encoder(data),
        errors=None,
    )


def error_response(message: str, errors=None, status_code: int = 400):
    return ApiResponse(
        success=False,
        message=message,
        status_code=status_code,
        data=None,
        errors=errors,
    )
