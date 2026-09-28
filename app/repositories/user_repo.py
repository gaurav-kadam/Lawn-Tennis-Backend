from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role
from app.utils.logger import logger
from app.utils.soft_delete import SoftDeleteHelper
from app.exceptions.db_safety import safe_commit


class UserRepository:

    @staticmethod
    def create_user(db: Session, user_data: dict):
        logger.info(f"Creating user in database: {user_data.get('email')}")
        user = User(**user_data)
        db.add(user)
        return safe_commit(db, user, "create_user")

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email, User.is_deleted == False).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int | None = None):
        query = db.query(User).filter(User.is_deleted == False)
        if skip or limit is not None:
            query = query.order_by(User.id).offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def get_all_roles(db: Session):
        return db.query(Role).all()

    @staticmethod
    def update_user(db: Session, existing_user: User, update_data: dict):
        for key, value in update_data.items():
            setattr(existing_user, key, value)
        return safe_commit(db, existing_user, "update_user")

    @staticmethod
    def delete_user(db: Session, user: User, deleted_by: int | None = None):
        return SoftDeleteHelper.soft_delete(db, user, deleted_by)

    @staticmethod
    def restore_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return SoftDeleteHelper.restore(db, user)
