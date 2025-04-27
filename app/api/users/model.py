from http.client import HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.database import get_supabase_client

supabase = get_supabase_client()

from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    """
    Data model for creating a new user.
    """
    name: str = Field(..., description="Full name of the user")
    email: str = Field(..., description="Email address of the user")
    birthdate: date = Field(..., description="User's birth date in YYYY-MM-DD format")
    school: str = Field(..., description="Name of the user's school")
    password: str = Field(..., description="User password", min_length=8)
    confirm_password: str = Field(..., description="Confirm password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


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
    auth_id: Optional[str] = None  # Add auth_id field to the response


class UserUpdate(BaseModel):
    """
    Data model for updating a user.
    """
    name: Optional[str] = None
    email: Optional[str] = None
    birthdate: Optional[date] = None
    school: Optional[str] = None

# -------------------------------------
# ----------- Chat Models -----------
# -------------------------------------

class ChatCreate(BaseModel):
    """
    Data model for creating a new chat.
    """
    user_id: str = Field(..., description="Email of the user")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Chat messages in JSON format")

class ChatResponse(BaseModel):
    """
    Data model for chat response.
    """
    chat_id: int
    user_id: str
    messages: List[Dict[str, Any]]
    date: datetime

class ChatUpdate(BaseModel):
    """
    Data model for updating a chat.
    """
    messages: Optional[List[Dict[str, Any]]] = None

class MessageCreate(BaseModel):
    """
    Data model for creating a new message in a chat.
    """
    content: str = Field(..., description="Message content")
    sender: str = Field(..., description="Message sender (user or system)")