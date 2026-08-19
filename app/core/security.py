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
    """
    Uses the `bcrypt` library directly rather than passlib's bcrypt wrapper.
    passlib 1.7.x ships a self-test (detect_wrap_bug) that is incompatible
    with bcrypt >= 4.1 and raises ValueError on every single hash/verify call
    - a real production landmine (password hashing, i.e. register/login,
    would be completely broken). Calling bcrypt directly avoids that broken
    compatibility shim entirely while keeping the exact same hash format
    ($2b$...), so existing stored hashes remain valid either way.
    """
    validate_password(password)
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    validate_password(plain_password)
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed/corrupted stored hash - treat as "does not match" rather
        # than crashing the request with a 500.
        return False


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
