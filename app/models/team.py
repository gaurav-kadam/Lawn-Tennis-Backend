from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)

    team_code = Column(String(50), unique=True, nullable=False)

    team_name = Column(String(150), nullable=False)
    short_name = Column(String(50), nullable=False)

    gender = Column(String(20), nullable=False)

    state = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)

    section = Column(String(100), nullable=False)

    head_coach = Column(String(150), nullable=False)
    coach = Column(String(150), nullable=False)
    manager = Column(String(150), nullable=False)

    player_file = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)