from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserRegister, UserLogin
from app.services.user_service import UserService
from app.utils.logger import logger
from app.responses.response_builder import success_response


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    logger.info(f"Registration request received for email: {user.email}")
    result = UserService.register_user(db, user)
    return success_response(
        message = "User registered successfully",
        data = result
    )


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login request received for email: {user.email}")
    result = UserService.login_user(db, user)
    return success_response(message = "Login successful", data = result)
