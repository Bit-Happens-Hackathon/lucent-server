from http.client import HTTPException
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import date
from database import get_supabase_client

supabase = get_supabase_client()

class UserCreate(BaseModel):
    """
    Data model for creating a new user.
    """
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Email address of the user")
    birthdate: date = Field(..., description="User's birth date in YYYY-MM-DD format")
    school: str = Field(..., description="Name of the user's school")


class UserResponse(BaseModel):
    """
    Data model for user response.
    """
    id: str
    name: str
    email: EmailStr
    birthdate: date
    school: str
    created_at: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Data model for updating a user.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    birthdate: Optional[date] = None
    school: Optional[str] = None
