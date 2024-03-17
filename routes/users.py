from typing import Annotated
from pydantic import Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from config.database import SessionLocal, get_db
from models.models import User, Role
from passlib.context import CryptContext

from schemas.schemas import CreateUserRequest


router = APIRouter(prefix="/users", tags=["users"])


db_dependency = Annotated[Session, Depends(get_db)]
