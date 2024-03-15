from typing import Annotated
from pydantic import Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from config.database import SessionLocal, get_db
from models.models import User, Role
from passlib.context import CryptContext

from schemas.schemas import CreateUserRequest


router = APIRouter(prefix="/admin", tags=["admin"])


db_dependency = Annotated[Session, Depends(get_db)]

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency):
    return db.query(User).all()


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):

    user_role = db.query(Role).filter(Role.role_name == "user").first()

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

    db.add(create_user_model)
    db.commit()
    return {"message": "User created successfully"}


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(db: db_dependency, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
