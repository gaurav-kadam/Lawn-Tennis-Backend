from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from app.db.base import Base


class Official(Base):
    __tablename__ = "officials"

    id = Column(Integer, primary_key=True, index=True)

    official_name = Column(String(150), nullable=False)
    official_code = Column(String(50), unique=True, nullable=False)
    role_title = Column(String(100), nullable=False, default="Official")

    mobile = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)