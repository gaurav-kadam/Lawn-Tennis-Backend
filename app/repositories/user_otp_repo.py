from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user_otp import UserOTP
from app.exceptions.db_safety import safe_commit
from app.utils.logger import logger


class UserOTPRepository:
    @staticmethod
    def create_otp(db: Session, user_id: int, otp: str, purpose: str, expires_at: datetime):
        otp_record = UserOTP(user_id=user_id, otp=otp, purpose=purpose, expires_at=expires_at)
        db.add(otp_record)
        safe_commit(db, otp_record, "create_otp")
        logger.info("OTP created successfully for user_id=%s", user_id)
        return otp_record

    @staticmethod
    def get_latest_active_otp(db: Session, user_id: int, purpose: str):
        return db.query(UserOTP).filter(
            UserOTP.user_id == user_id,
            UserOTP.purpose == purpose,
            UserOTP.is_used.is_(False),
            UserOTP.expires_at > datetime.utcnow()
        ).order_by(UserOTP.created_at.desc()).first()

    @staticmethod
    def mark_otp_used(db: Session, otp_record):
        otp_record.is_used = True
        safe_commit(db, otp_record, "mark_otp_used")
        logger.info("OTP marked as used for user_id=%s", otp_record.user_id)

    @staticmethod
    def invalidate_previous_otps(db: Session, user_id: int, purpose: str):
        records = db.query(UserOTP).filter(
            UserOTP.user_id == user_id,
            UserOTP.purpose == purpose,
            UserOTP.is_used.is_(False)
        ).all()
        if records:
            for record in records:
                record.is_used = True
            safe_commit(db, records[0], "invalidate_previous_otps")
            logger.info("Previous OTPs invalidated for user_id=%s", user_id)
