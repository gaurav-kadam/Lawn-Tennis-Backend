from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):

    success: bool
    message: str
    status_code: int = 200
    data: Optional[T] = None
    errors: Optional[list] = None