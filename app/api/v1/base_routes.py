from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService
from app.middleware.auth_middleware import require_roles
from app.responses.response_builder import success_response


router = APIRouter()
manage_users = require_roles()


@router.post("/users")
def create_user(user: UserCreate, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    result = UserService.create_user(db, user)
    return success_response(message = "User created successfully", data = result)


@router.get("/roles")
def get_roles(current_user=Depends(manage_users), db: Session = Depends(get_db)):
    roles = UserService.getAllRoles(db)
    return success_response(message = "Roles fetched successfully", data = roles)


@router.get("/users")
def get_users(current_user=Depends(manage_users), db: Session = Depends(get_db)):
    users = UserService.get_all_users(db)
    return success_response(message = "Users fetched successfully", data = users)



@router.get("/users/{user_id}")
def get_user(user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id)
    return success_response(message = "User fetched successfully", data = user)


@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    updated_user = UserService.update_user(db, user_id, user)
    return success_response(message = "User updated successfully", data = updated_user)


@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    deleted_by = current_user.get("user_id")
    UserService.delete_user(db, user_id, deleted_by)
    return success_response(message = "User deleted successfully")


@router.post("/users/{user_id}/restore")
def restore_user(user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    result = UserService.restore_user(db, user_id)
    return success_response(message = "User restored successfully", data = result)
