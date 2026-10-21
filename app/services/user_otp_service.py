from datetime import datetime, timedelta
import random

from sqlalchemy.orm import Session
from app.repositories.user_otp_repo import UserOTPRepository
from app.services.email_service import EmailService
from app.utils.logger import logger

from app.services.user_service import UserService
from app.core.security import create_access_token
from app.repositories.user_repo import UserRepository
from app.exceptions import AuthenticationException, NotFoundException
from app.services.refresh_token_service import RefreshTokenService

class UserOTPService:
    @staticmethod
    def generate_login_otp(db: Session, user):
        otp = str(random.randint(1000, 9999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        UserOTPRepository.invalidate_previous_otps(db, user.id, "login")
        UserOTPRepository.create_otp(db, user.id, otp, "login", expires_at)

        EmailService.send_login_otp_email(user.email, user.name, otp)
        logger.info("Login OTP sent successfully for user_id=%s", user.id)

        return {"message": "OTP sent successfully to your email."}

    @staticmethod
    def verify_login_otp(db: Session, email: str, otp: str):
        user = UserRepository.get_user_by_email(db, email)
        if not user:
            raise NotFoundException("User not found")

        otp_record = UserOTPRepository.get_latest_active_otp(db, user.id, "login")
        if not otp_record or otp_record.otp != otp:
            raise AuthenticationException("Invalid OTP")

        if otp_record.expires_at < datetime.utcnow():
            raise AuthenticationException("OTP has expired")

        UserOTPRepository.mark_otp_used(db, otp_record)

        access_token = create_access_token({
            "user_id": user.id,
            "email": user.email,
            "role_name": user.role.role_name if user.role else None
        })
        refresh_token = RefreshTokenService.create_refresh_token_for_user(db, user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": UserService._build_user_response(user)
        }
