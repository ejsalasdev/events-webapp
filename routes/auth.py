from datetime import timedelta, datetime, timezone
from typing import Annotated
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, status
from config.database import get_db
from models.models import User, Role
from .common import get_user_by_identification
from schemas.schemas import CreateUserRequest, Token, LoginRequest
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["auth"])

db_dependency = Annotated[Session, Depends(get_db)]

pwd_context = CryptContext(schemes=["argon2"], argon2__type="ID", deprecated="auto")

SECRET_KEY = "41Hcg7wVEtauHAvQp3Veaopizpk+NqCSacwYGKaK7Ng="
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def authenticate_user(db: db_dependency, login_user_data: LoginRequest):
    user = db.query(User).filter(User.username == login_user_data.username).first()
    if not user:
        return False
    if not pwd_context.verify(login_user_data.password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int):
    to_encode = {"sub": username, "id": user_id}
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    db: db_dependency, token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise credentials_exception
        user = (
            db.query(User)
            .filter(User.username == username)
            .options(joinedload(User.role))
            .first()
        )
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user


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
        username=create_user_request.username,
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


"""
@router.put("/change_password/{user_id}", status_code=status.HTTP_200_OK)
async def change_password(db: db_dependency, user_id: int, password: str):
    user = get_user_by_identification(db, user_id)
    user.hashed_password = pwd_context.hash(password)

    try:
        db.commit()
        db.refresh(user)
        return {"message": "Password changed successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while changing the password: {e}",
        )
"""


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(
        db, LoginRequest(username=form_data.username, password=form_data.password)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user.username, user.id)
    return {"access_token": access_token, "token_type": "bearer"}
