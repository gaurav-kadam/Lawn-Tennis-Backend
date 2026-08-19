from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from app.db.base import Base


class Official(Base):
    __tablename__ = "officials"

    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    official_name = Column(String(150), nullable=False)
    official_code = Column(String(50), unique=True, nullable=False)
    role_title = Column(String(100), nullable=False, default="Official")

    # Contact information
    mobile = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    # Location
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)

    # Personal information
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)