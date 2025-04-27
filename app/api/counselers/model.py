from typing import Optional
from pydantic import BaseModel, Field

class CounselorCreate(BaseModel):
    """
    Data model for creating a new counselor.
    """
    name: str = Field(..., description="Name of the counselor")
    description: str = Field(..., description="Description of the counselor")
    email: str = Field(..., description="Email of the counselor")
    photo_url: str = Field(..., description="URL to the counselor's photo")
    link: Optional[str] = Field(None, description="Link to the counselor's profile")
    school_id: str = Field(..., description="School name")

class CounselorResponse(BaseModel):
    """
    Data model for counselor response.
    """
    id: int
    name: str
    description: str
    email: str
    photo_url: str
    link: Optional[str] = None
    school_id: str

class CounselorUpdate(BaseModel):
    """
    Data model for updating a counselor.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None
    link: Optional[str] = None
    school_id: Optional[str] = None