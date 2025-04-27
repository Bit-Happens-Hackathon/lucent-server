from typing import Optional
from pydantic import BaseModel, Field, conint
from datetime import date

class UserWellnessCreate(BaseModel):
    """
    Data model for creating a new user wellness record.
    """
    user_id: str = Field(..., description="Email of the user")
    record_date: Optional[date] = Field(None, description="Date of wellness record")
    physical: int = Field(..., description="Physical wellness score (0-100)", ge=0, le=100)
    financial: int = Field(..., description="Financial wellness score (0-100)", ge=0, le=100)
    emotional: int = Field(..., description="Emotional wellness score (0-100)", ge=0, le=100)
    spiritual: int = Field(..., description="Spiritual wellness score (0-100)", ge=0, le=100)
    social: int = Field(..., description="Social wellness score (0-100)", ge=0, le=100)
    environmental: int = Field(..., description="Environmental wellness score (0-100)", ge=0, le=100)
    creative: int = Field(..., description="Creative wellness score (0-100)", ge=0, le=100)
    

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
    record_date: Optional[date] = None  # Renamed from 'date' to 'record_date'
    physical: Optional[int] = Field(None, description="Physical wellness score (0-100)", ge=0, le=100)
    financial: Optional[int] = Field(None, description="Financial wellness score (0-100)", ge=0, le=100)
    emotional: Optional[int] = Field(None, description="Emotional wellness score (0-100)", ge=0, le=100)
    spiritual: Optional[int] = Field(None, description="Spiritual wellness score (0-100)", ge=0, le=100)
    social: Optional[int] = Field(None, description="Social wellness score (0-100)", ge=0, le=100)
    environmental: Optional[int] = Field(None, description="Environmental wellness score (0-100)", ge=0, le=100)
    creative: Optional[int] = Field(None, description="Creative wellness score (0-100)", ge=0, le=100)