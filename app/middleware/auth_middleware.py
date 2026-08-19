from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.exceptions import AuthenticationException, AuthorizationException


security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Authentication - proves WHO the caller is. Returns the decoded token payload
    (user_id, email, role_name)."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise AuthenticationException("Invalid or expired token")

    # A validly-signed token that is missing required claims (e.g. one issued
    # by an older/different code path, or a tampered/hand-crafted payload
    # that still happens to verify) must still be rejected - don't let
    # downstream code silently treat a missing role_name as "no role".
    if not payload.get("user_id") or not payload.get("role_name"):
        raise AuthenticationException("Invalid or expired token")

    return payload


def require_roles(*allowed_roles: str):
    """
    Authorization - proves WHAT the caller is allowed to do, on top of a valid token.

    Usage:
        @router.delete("/tournaments/{id}")
        def delete_tournament(..., current_user=Depends(require_roles("Admin", "Supervisor"))):
            ...

    "Supervisor" always has full access across the app, matching the frontend's
    canAccessMenu rule (Supervisor sees/does everything). Every other role must be
    explicitly listed at each protected endpoint.
    """
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
