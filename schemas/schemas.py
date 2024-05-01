from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Schema for user full registration
class CreateUserRequest(BaseModel):
    identification: str = Field(
        min_length=5,
        max_length=10,
        description="User's identification number, between 5 and 10 digits long",
    )
    first_name: str = Field(
        min_length=3, max_length=15, description="User's first name"
    )
    last_name: str = Field(min_length=3, max_length=15, description="User's last name")
    phone_number: str = Field(
        min_length=10,
        max_length=10,
        description="User's phone number, 10 digits long",
    )
    email: EmailStr = Field(description="User's email address")
    username: Optional[str] = Field(None, description="User's username, optional")
    password: Optional[str] = Field(None, description="User's password, optional")
    role: Optional[str] = Field(None, description="User's role, optional")


# Schema for user data update
class UserUpdateRequest(BaseModel):
    identification: Optional[str] = Field(
        None,
        min_length=5,
        max_length=10,
        description="User's identification number, between 5 and 10 digits long",
    )
    first_name: Optional[str] = Field(
        None, min_length=3, description="User's first name"
    )
    last_name: Optional[str] = Field(None, min_length=3, description="User's last name")
    phone_number: Optional[str] = Field(
        None,
        min_length=10,
        max_length=10,
        description="User's phone number, 10 digits long",
    )
    email: Optional[EmailStr] = Field(None, description="User's email address")


# Schema for user login
class LoginRequest(BaseModel):
    username: str = Field(description="User's username")
    password: str = Field(description="User's password")


# Schema for token
class Token(BaseModel):
    access_token: str
    token_type: str
