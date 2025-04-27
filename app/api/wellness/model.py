from typing import Optional
from pydantic import BaseModel, Field
from datetime import date

class UserWellnessCreate(BaseModel):
    """
    Data model for creating a new user wellness record.
    """
    user_id: str = Field(..., description="Email of the user")
    date: Optional[date] = Field(None, description="Date of wellness record")
    physical: int = Field(..., ge=0, le=100, description="Physical wellness score (0-100)")
    financial: int = Field(..., ge=0, le=100, description="Financial wellness score (0-100)")
    emotional: int = Field(..., ge=0, le=100, description="Emotional wellness score (0-100)")
    spiritual: int = Field(..., ge=0, le=100, description="Spiritual wellness score (0-100)")
    social: int = Field(..., ge=0, le=100, description="Social wellness score (0-100)")
    environmental: int = Field(..., ge=0, le=100, description="Environmental wellness score (0-100)")
    creative: int = Field(..., ge=0, le=100, description="Creative wellness score (0-100)")

class UserWellnessResponse(BaseModel):
    """
    Data model for user wellness response.
    """
    wellness_id: int
    user_id: str
    date: date
    physical: int
    financial: int
    emotional: int
    spiritual: int
    social: int
    environmental: int
    creative: int

class UserWellnessUpdate(BaseModel):
    """
    Data model for updating a user wellness record.
    """
    date: Optional[date] = None
    physical: Optional[int] = Field(None, ge=0, le=100)
    financial: Optional[int] = Field(None, ge=0, le=100)
    emotional: Optional[int] = Field(None, ge=0, le=100)
    spiritual: Optional[int] = Field(None, ge=0, le=100)
    social: Optional[int] = Field(None, ge=0, le=100)
    environmental: Optional[int] = Field(None, ge=0, le=100)
    creative: Optional[int] = Field(None, ge=0, le=100)