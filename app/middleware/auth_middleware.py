from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.exceptions import AuthenticationException, AuthorizationException


security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise AuthenticationException("Invalid or expired token")
    if not payload.get("user_id") or not payload.get("role_name"):
        raise AuthenticationException("Invalid or expired token")

    return payload


def require_roles(*allowed_roles: str):

    def checker(current_user: dict = Depends(verify_token)):
        role_name = current_user.get("role_name")

        if role_name == "Supervisor":
            return current_user

        if role_name not in allowed_roles:
            raise AuthorizationException(
                message=f"Role '{role_name}' is not permitted to perform this action"
            )

        return current_user

    return checker
