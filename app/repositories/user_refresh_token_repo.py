from sqlalchemy.orm import Session
from app.exceptions.db_safety import safe_commit
from app.models.user_refresh_token import UserRefreshToken
from app.utils.logger import logger


class UserRefreshTokenRepository:
    @staticmethod
    def create_refresh_token(db: Session, token_data: dict):
        refresh_token = UserRefreshToken(**token_data)
        db.add(refresh_token)
        saved_token = safe_commit(db, refresh_token, "create_refresh_token")
        logger.info("Refresh token created successfully for user_id=%s", saved_token.user_id)
        return saved_token

    @staticmethod
    def get_by_token_hash(db: Session, token_hash: str):
        return db.query(UserRefreshToken).filter(
            UserRefreshToken.token_hash == token_hash,
            UserRefreshToken.is_revoked.is_(False)
        ).first()