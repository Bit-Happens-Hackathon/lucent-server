from typing import Optional
from pydantic import BaseModel, Field

class SchoolCreate(BaseModel):
    """
    Data model for creating a new school.
    """
    name: str = Field(..., description="Name of the school")

class SchoolResponse(BaseModel):
    """
    Data model for school response.
    """
    name: str

class SchoolUpdate(BaseModel):
    """
    Data model for updating a school.
    """
    name: Optional[str] = None