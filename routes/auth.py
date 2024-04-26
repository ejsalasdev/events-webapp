from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from admin import pwd_context
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer


router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "41Hcg7wVEtauHAvQp3Veaopizpk+NqCSacwYGKaK7Ng="
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)
