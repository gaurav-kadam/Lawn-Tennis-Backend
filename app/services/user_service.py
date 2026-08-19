from sqlalchemy.orm import Session
from app.exceptions import NotFoundException, ConflictException, BadRequestException, AuthenticationException

from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserRegister, UserLogin, UserUpdate

from app.core.security import hash_password, verify_password, create_access_token
from app.utils.logger import logger

# Role every public self-registration is forced into - the least-privileged
# role in the system. Never trust a role coming from an unauthenticated caller.
DEFAULT_PUBLIC_ROLE = "Scorer"


class UserService:

    @staticmethod
    def _build_user_response(user):
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": {
                "role_id": user.role.role_id,
                "role_name": user.role.role_name,
                "is_active": user.role.is_active,
            } if user.role else None,
        }

    @staticmethod
    def register_user(db: Session, user: UserRegister):
        logger.info(f"Checking existing user for email: {user.email}")
        existing_user = UserRepository.get_user_by_email(db, user.email)
        if existing_user:
            logger.warning(f"Registration failed. Email already exists: {user.email}")
            raise ConflictException("Email already exists")

        default_role = next(
            (r for r in UserRepository.get_all_roles(db) if r.role_name == DEFAULT_PUBLIC_ROLE),
            None,
        )
        if not default_role:
            # Should never happen (roles are seeded on startup) but fail safely rather
            # than silently falling back to some other role.
            logger.error(f"Default public role '{DEFAULT_PUBLIC_ROLE}' not found while registering {user.email}")
            raise BadRequestException("Registration is temporarily unavailable. Please try again later.")

        hashed_password = hash_password(user.password)
        created_user = UserRepository.create_user(db, {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "role_id": default_role.role_id,
        })

        return UserService._build_user_response(created_user)

    @staticmethod
    def create_user(db: Session, user: UserCreate):
        """Admin-created user (POST /users - Supervisor only). role_id is trusted
        because the caller was already authenticated + authorized as Supervisor."""
        logger.info(f"Checking existing user for email: {user.email}")
        existing_user = UserRepository.get_user_by_email(db, user.email)
        if existing_user:
            logger.warning(f"User creation failed. Email already exists: {user.email}")
            raise ConflictException("Email already exists")

        hashed_password = hash_password(user.password)
        created_user = UserRepository.create_user(db, {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "role_id": user.role_id,
        })

        return UserService._build_user_response(created_user)

    @staticmethod
    def login_user(db: Session, user: UserLogin):
        logger.info(f"Login attempt started for: {user.email}")
        existing_user = UserRepository.get_user_by_email(db, user.email)
        if not existing_user:
            logger.warning(f"Login failed. User not found: {user.email}")
            raise AuthenticationException("Invalid email or password")

        if not verify_password(user.password, existing_user.password):
            logger.warning(f"Invalid password attempt for: {user.email}")
            raise AuthenticationException("Invalid email or password")

        role_name = existing_user.role.role_name if existing_user.role else None

        token = create_access_token({
            "user_id": existing_user.id,
            "email": existing_user.email,
            "role_name": role_name,
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": existing_user.id,
                "name": existing_user.name,
                "email": existing_user.email,
                "role": {
                    "role_id": existing_user.role.role_id,
                    "role_name": existing_user.role.role_name,
                    "is_active": existing_user.role.is_active
                } if existing_user.role else None
            }
        }

    @staticmethod
    def get_all_users(db: Session):
        users = UserRepository.get_all_users(db)
        return [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": {
                    "role_id": u.role.role_id,
                    "role_name": u.role.role_name,
                    "is_active": u.role.is_active
                } if u.role else None
            }
            for u in users
        ]

    @staticmethod
    def getAllRoles(db: Session):
        return UserRepository.get_all_roles(db)

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate):
        existing_user = UserRepository.get_user_by_id(db, user_id)
        if not existing_user:
            raise NotFoundException("User not found")
        update_data = user_data.model_dump(exclude_unset=True)
        return UserRepository.update_user(db, existing_user, update_data)

    @staticmethod
    def delete_user(db: Session, user_id: int, deleted_by: int | None = None):
        existing_user = UserRepository.get_user_by_id(db, user_id)
        if not existing_user:
            raise NotFoundException("User not found")
        UserRepository.delete_user(db, existing_user, deleted_by)
        return True

    @staticmethod
    def restore_user(db: Session, user_id: int):
        result = UserRepository.restore_user(db, user_id)
        if result is None:
            raise NotFoundException("User not found")
        return result
