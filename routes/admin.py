from typing import Annotated
from pydantic import Field
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from config.database import get_db
from models.models import User
from .auth import get_current_user
from .common import get_user_by_identification
from schemas.schemas import UserUpdateRequest


router = APIRouter(prefix="/admin", tags=["admin"])

# This dependency is used to get a database session.
db_dependency = Annotated[Session, Depends(get_db)]
# This dependency is used to get a validate admin.
user_admin_dependency = Annotated[User, Depends(get_current_user)]


# This function is used to get a validate admin.
def get_admin(user_admin: User):
    admin_role = any(role.role_name == "admin" for role in user_admin.role)
    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    return user_admin


# This function is used to get all users.
@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency, user: user_admin_dependency):
    get_admin(user)

    return db.query(User).options(joinedload(User.role)).all()


# This function is used to get a unique user by identification.
@router.get("/{user_identification}", status_code=status.HTTP_200_OK)
async def get_user(
    db: db_dependency, user_identification: str, user: user_admin_dependency
):
    get_admin(user)
    return get_user_by_identification(db, user_identification)


# This function is used to update a user.
@router.put("/{user_identification}", status_code=status.HTTP_200_OK)
async def update_user(
    db: db_dependency,
    user_identification: str,
    user_update_request: UserUpdateRequest,
    user: user_admin_dependency,
):
    get_admin(user)
    user_to_update = get_user_by_identification(db, user_identification)

    update_data = user_update_request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_to_update, key, value)

    try:
        db.commit()
        db.refresh(user_to_update)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the user: {e}",
        )

    return {"message": "User updated successfully"}


# This function is used to delete a user.
@router.delete("/{user_identification}", status_code=status.HTTP_200_OK)
async def delete_user(
    db: db_dependency, user_identification: str, user: user_admin_dependency
):
    get_admin(user)

    user_to_delete = get_user_by_identification(db, user_identification)

    try:
        db.delete(user_to_delete)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the user: {e}",
        )

    return {"message": "User deleted successfully"}
