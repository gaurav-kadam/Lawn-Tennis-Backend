from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService
from app.middleware.auth_middleware import require_roles

router = APIRouter()

# User & role management is sensitive (can create Admins, delete accounts) -
# Supervisor only. require_roles() with no extra roles listed means "Supervisor
# only" (Supervisor always passes; every other role is rejected).
manage_users = require_roles()


@router.post("/users")
def create_user(user: UserCreate, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    result = UserService.create_user(db, user)
    return {"message": "User created successfully", "logged_in_user": current_user, "data": result}


@router.get("/roles")
def get_roles(current_user=Depends(manage_users), db: Session = Depends(get_db)):
    roles = UserService.getAllRoles(db)
    return {"message": "Roles fetched successfully", "logged_in_user": current_user, "data": roles}


@router.get("/users")
def get_users(current_user=Depends(manage_users), db: Session = Depends(get_db)):
    users = UserService.get_all_users(db)
    return {"message": "Users fetched successfully", "logged_in_user": current_user, "data": users}


@router.get("/users/{user_id}")
def get_user(user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    user = UserService.get_user_by_id(db, user_id)
    return {"message": "User fetched successfully", "logged_in_user": current_user, "data": user}


@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    updated_user = UserService.update_user(db, user_id, user)
    return {"message": "User updated successfully", "logged_in_user": current_user, "data": updated_user}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    deleted_by = current_user.get("user_id")
    UserService.delete_user(db, user_id, deleted_by)
    return {"message": "User deleted successfully", "logged_in_user": current_user}


@router.post("/users/{user_id}/restore")
def restore_user(user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)):
    result = UserService.restore_user(db, user_id)
    return {"message": "User restored successfully", "logged_in_user": current_user, "data": result}
