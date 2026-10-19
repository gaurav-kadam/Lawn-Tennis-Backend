from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Boolean,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserRefreshToken(Base):
    __tablename__ = "user_refresh_token"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    token_hash = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User")