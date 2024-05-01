from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from config.database import get_db
from models.models import User, Role
from schemas.schemas import CreateUserRequest


router = APIRouter(prefix="/users", tags=["users"])


db_dependency = Annotated[Session, Depends(get_db)]


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
