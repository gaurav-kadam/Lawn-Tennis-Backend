from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import (
    create_refresh_token,
    hash_refresh_token,
    get_refresh_token_expiry,
    create_access_token,
)
from app.repositories.user_refresh_token_repo import (
    UserRefreshTokenRepository,
)
from app.repositories.user_repo import UserRepository

from app.exceptions.custom_exceptions import (
    AuthenticationException,
    NotFoundException,
)
from app.utils.logger import logger


class RefreshTokenService:

    @staticmethod
    def create_refresh_token_for_user(
            db: Session,
            user_id: int,
    ):
        refresh_token = create_refresh_token()

        token_hash = hash_refresh_token(refresh_token)
        expires_at = get_refresh_token_expiry()

        UserRefreshTokenRepository.create_refresh_token(
            db=db,
            token_data={
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": expires_at,
                "is_revoked": False,
            },
        )

        logger.info(
            f"Refresh token created for user_id: {user_id}"
        )
        return refresh_token

    @staticmethod
    def refresh_access_token(
            db: Session,
            refresh_token: str,
    ):
        token_hash = hash_refresh_token(refresh_token)

        stored_token = (
            UserRefreshTokenRepository.get_by_token_hash(
                db=db,
                token_hash=token_hash,
            )
        )

        if not stored_token:
            logger.warning("Invalid or revoked refresh token")
            raise AuthenticationException(
                "Invalid refresh token"
            )

        if stored_token.expires_at < datetime.utcnow():
            logger.warning(
                "Expired refresh token for "
                f"user_id: {stored_token.user_id}"
            )
            raise AuthenticationException(
                "Refresh token has expired"
            )

        user = UserRepository.get_user_by_id(
            db,
            stored_token.user_id,
        )

        if not user:
            raise NotFoundException("User not found")

        role_name = user.role.role_name if user.role else None

        access_token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "role_name": role_name,
            }
        )

        logger.info(
            "New access token generated for "
            f"user_id: {user.id}"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }