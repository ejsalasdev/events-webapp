from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.models import User


# This function is used to get a user by identification.
def get_user_by_identification(db: Session, user_identification: str):
    user = db.query(User).filter(User.identification == user_identification).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
