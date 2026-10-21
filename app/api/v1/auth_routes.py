from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserRegister, UserLogin, UserOTPVerify
from app.services.user_service import UserService
from app.services.user_otp_service import UserOTPService
from app.utils.logger import logger
from app.responses.response_builder import success_response
from app.schemas.refresh_token import RefreshTokenRequest
from app.services.refresh_token_service import RefreshTokenService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    logger.info(f"Registration request received for email: {user.email}")
    result = UserService.register_user(db, user)
    return success_response(message="User registered successfully", data=result)


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login request received for email: {user.email}")
    result = UserService.login_user(db, user)
    return success_response(message="OTP sent successfully", data=result)

@router.post("/refresh")
def refresh_access_token(
        request: RefreshTokenRequest,
        db: Session = Depends(get_db),
):
    result = RefreshTokenService.refresh_access_token(
        db=db,
        refresh_token=request.refresh_token,
    )

    return success_response(
        message="Access token refreshed successfully",
        data=result,
    )
@router.post("/verify-otp")
def verify_login_otp(
        request: UserOTPVerify,
        db: Session = Depends(get_db),
):
    result = UserOTPService.verify_login_otp(
        db=db,
        email=request.email,
        otp=request.otp,
    )

    return success_response(
        message="Login successful",
        data=result,
    )
