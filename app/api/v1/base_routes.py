from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService
from app.middleware.auth_middleware import require_roles
from app.responses.response_builder import success_response

router = APIRouter()
manage_users = require_roles()


@router.post("/user")
def create_user(
    user: UserCreate, current_user=Depends(manage_users), db: Session = Depends(get_db)
):
    result = UserService.create_user(db, user)
    return success_response(message="User created successfully", data=result)


@router.get("/roles")
def get_roles(current_user=Depends(manage_users), db: Session = Depends(get_db)):
    roles = UserService.get_all_roles(db)
    return success_response(message="Roles fetched successfully", data=roles)


@router.get("/users")
def get_users(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1),
        current_user=Depends(manage_users),
        db: Session = Depends(get_db),
):
    users, total = UserService.get_all_users(db, page, page_size)

    return success_response(
        message="Users fetched successfully",
        data={
            "items": users,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    )

@router.get("/user/{user_id}")
def get_user(
    user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)
):
    user = UserService.get_user_by_id(db, user_id)
    return success_response(
        message="User fetched successfully",
        data=jsonable_encoder(user, exclude={"password"}),
    )


@router.put("/user/{user_id}")
def update_user(
    user_id: int,
    user: UserUpdate,
    current_user=Depends(manage_users),
    db: Session = Depends(get_db),
):
    updated_user = UserService.update_user(db, user_id, user)
    return success_response(
        message="User updated successfully",
        data=jsonable_encoder(updated_user, exclude={"password"}),
    )


@router.delete("/user/{user_id}")
def delete_user(
    user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)
):
    deleted_by = current_user.get("user_id")
    UserService.delete_user(db, user_id, deleted_by)
    return success_response(message="User deleted successfully")


@router.post("/user/{user_id}/restore")
def restore_user(
    user_id: int, current_user=Depends(manage_users), db: Session = Depends(get_db)
):
    result = UserService.restore_user(db, user_id)
    return success_response(
        message="User restored successfully",
        data=jsonable_encoder(result, exclude={"password"}),
    )
