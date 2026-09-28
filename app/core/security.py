from datetime import datetime, timedelta

import bcrypt
from jose import jwt
from app.core.config import settings
from app.exceptions import BadRequestException

MAX_PASSWORD_BYTES = 72


def validate_password(password: str):
    if len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
        raise BadRequestException("Password must be 72 bytes or less")


def hash_password(password: str) -> str:
    validate_password(password)
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    validate_password(plain_password)
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
