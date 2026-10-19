from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.user_refresh_token import UserRefreshToken
from app.utils.logger import logger
from app.exceptions.custom_exceptions import DatabaseException


class UserRefreshTokenRepository:

    @staticmethod
    def create_refresh_token(
            db: Session,
            token_data: dict,
    ):
        try:
            refresh_token = UserRefreshToken(**token_data)

            db.add(refresh_token)
            db.commit()
            db.refresh(refresh_token)

            return refresh_token

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Database error while creating refresh token"
            )

            raise DatabaseException(
                "Failed to create refresh token"
            )

    @staticmethod
    def get_by_token_hash(
            db: Session,
            token_hash: str,
    ):
        try:
            return (
                db.query(UserRefreshToken)
                .filter(
                    UserRefreshToken.token_hash == token_hash,
                    UserRefreshToken.is_revoked.is_(False),
                    )
                .first()
            )

        except SQLAlchemyError:
            logger.exception(
                "Database error while fetching refresh token"
            )

            raise DatabaseException(
                "Failed to fetch refresh token"
            )