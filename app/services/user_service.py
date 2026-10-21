from sqlalchemy.orm import Session
from app.exceptions import NotFoundException, ConflictException, BadRequestException, AuthenticationException

from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate, UserRegister, UserLogin, UserUpdate

from app.core.security import hash_password, verify_password, create_access_token
from app.utils.logger import logger
from app.services.refresh_token_service import RefreshTokenService
from app.services.email_service import EmailService

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
            logger.error(f"Default public role '{DEFAULT_PUBLIC_ROLE}' not found while registering {user.email}")
            raise BadRequestException("Registration is temporarily unavailable. Please try again later.")

        hashed_password = hash_password(user.password)
        created_user = UserRepository.create_user(db, {
            "name": user.name,
            "email": user.email,
            "password": hashed_password,
            "role_id": default_role.role_id,
        })

        try:
            EmailService.send_registration_email(
                to=created_user.email,
                user_name=created_user.name,
            )

            logger.info(
                f"Registration email sent: {created_user.email}"
            )

        except Exception:
            logger.exception(
                f"Registration email failed: {created_user.email}"
            )

        return UserService._build_user_response(created_user)

    @staticmethod
    def create_user(db: Session, user: UserCreate):
        logger.info(f"Checking existing user for email: {user.email}")
        existing_user = UserRepository.get_user_by_email(db, user.email)
        if existing_user:
            logger.warning(f"User creation failed. Email already exists: {user.email}")
            raise ConflictException("Email already exists")

        if not any(role.role_id == user.role_id for role in UserRepository.get_all_roles(db)):
            raise BadRequestException("Invalid role")

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
        logger.info("Login attempt started for: %s", user.email)
        existing_user = UserRepository.get_user_by_email(db, user.email)

        if not existing_user or not verify_password(user.password, existing_user.password):
            logger.warning("Login failed for: %s", user.email)
            raise AuthenticationException("Invalid email or password")

        from app.services.user_otp_service import UserOTPService
        return UserOTPService.generate_login_otp(db, existing_user)

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int | None = None):
        users = UserRepository.get_all_users(db, skip, limit)
        return [UserService._build_user_response(user) for user in users]

    @staticmethod
    def get_all_roles(db: Session):
        return UserRepository.get_all_roles(db)

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate):
        existing_user = UserService.get_user_by_id(db, user_id)
        update_data = user_data.model_dump(exclude_unset=True)
        return UserRepository.update_user(db, existing_user, update_data)

    @staticmethod
    def delete_user(db: Session, user_id: int, deleted_by: int | None = None):
        existing_user = UserService.get_user_by_id(db, user_id)
        UserRepository.delete_user(db, existing_user, deleted_by)
        return True

    @staticmethod
    def restore_user(db: Session, user_id: int):
        result = UserRepository.restore_user(db, user_id)
        if result is None:
            raise NotFoundException("User not found")
        return result
