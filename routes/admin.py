from typing import Annotated
from pydantic import Field
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from config.database import SessionLocal, get_db
from models.models import User, Role
from passlib.context import CryptContext

from schemas.schemas import CreateUserRequest, UserUpdateRequest


router = APIRouter(prefix="/admin", tags=["admin"])

# This dependency is used to get a database session.
db_dependency = Annotated[Session, Depends(get_db)]

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# This function is used to get a user by id.
def get_user_by_id(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency):
    return db.query(User).options(joinedload(User.role)).all()


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user_id: int):
    return get_user_by_id(db, user_id)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):

    user_role = db.query(Role).filter(Role.role_name == "admin").first()

    if not user_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User role not found"
        )

    create_user_model = User(
        identification=create_user_request.identification,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        phone_number=create_user_request.phone_number,
        email=create_user_request.email,
        hashed_password=pwd_context.hash(create_user_request.password),
        role=[user_role],
    )

    try:
        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the user: {e}",
        )

    return {"message": "User created successfully"}


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(
    db: db_dependency, user_id: int, user_update_request: UserUpdateRequest
):
    user_to_update = get_user_by_id(db, user_id)

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


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(db: db_dependency, user_id: int):

    user_to_delete = get_user_by_id(db, user_id)

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
