from app.exceptions.base import AppException
from app.exceptions.custom_exceptions import (
    NotFoundException,
    ConflictException,
    BadRequestException,
    AuthenticationException,
    AuthorizationException,
    DatabaseException,
    InternalServerException,
)
from app.exceptions.handlers import register_exception_handlers
from app.exceptions.db_safety import safe_commit, safe_delete, safe_query_delete, transaction
