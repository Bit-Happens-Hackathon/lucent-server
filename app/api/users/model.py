from http.client import HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from app.database import get_supabase_client

supabase = get_supabase_client()

class UserCreate(BaseModel):
    """
    Data model for creating a new user.
    """
    name: str = Field(..., description="Full name of the user")
    email: str = Field(..., description="Email address of the user")
    birthdate: date = Field(..., description="User's birth date in YYYY-MM-DD format")
    school: str = Field(..., description="Name of the user's school")


class UserResponse(BaseModel):
    """
    Data model for user response.
    """
    id: str
    name: str
    email: str
    birthdate: date
    school: str
    created_at: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Data model for updating a user.
    """
    name: Optional[str] = None
    email: Optional[str] = None
    birthdate: Optional[date] = None
    school: Optional[str] = None
