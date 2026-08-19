from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime
from app.db.base import Base


class Tournament(Base):
    __tablename__ = "tournament"

    id = Column(Integer, primary_key=True, index=True)
    tournament_name = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    state = Column(String(100))
    city = Column(String(100))
    venue = Column(String(255))
    section = Column(String(100))
    gender = Column(String(50))
    is_active = Column(Boolean, default=True, nullable=False)
    tournament_code = Column(String(50), unique=True, nullable=False)

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)
