from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from app.db.base import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)

    player_name = Column(String(150), nullable=False)
    player_code = Column(String(50), unique=True, nullable=False)

    age = Column(Integer)
    gender = Column(String(20))

    weight = Column(Float, nullable=True)
    category = Column(String(50), nullable=True)

    state = Column(String(100))
    city = Column(String(100))
    mobile = Column(String(20))
    ranking = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)