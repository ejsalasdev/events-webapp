from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    identification: str = Field(
        min_length=5,
        max_length=10,
        description="User's identification number, between 5 and 10 digits long",
    )
    first_name: str = Field(min_length=3, description="User's first name")
    last_name: str = Field(min_length=3, description="User's last name")
    phone_number: str = Field(
        min_length=10,
        max_length=10,
        description="User's phone number, 10 digits long",
    )
    email: EmailStr = Field(description="User's email address")
    password: Optional[str] = Field(None, description="User's password, optional")
    role: Optional[str] = Field(None, description="User's role, optional")
