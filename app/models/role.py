from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base


class Role(Base):
    __tablename__ = "tbl_role"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
