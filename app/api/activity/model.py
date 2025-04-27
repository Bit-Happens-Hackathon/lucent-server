from http.client import HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.database import get_supabase_client

supabase = get_supabase_client()

class ActivityCreate(BaseModel):
    """
    Data model for creating a new user activity.
    """
    user_id: str = Field(..., description="Email of the user")
    login: Optional[datetime] = Field(default_factory=datetime.now, description="Login timestamp")


class ActivityResponse(BaseModel):
    """
    Data model for activity response.
    """
    activity_id: int
    user_id: str
    login: datetime
    created_at: Optional[str] = None


class ActivityUpdate(BaseModel):
    """
    Data model for updating an activity.
    """
    user_id: Optional[str] = None
    login: Optional[datetime] = None