from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date 
from app.database import get_supabase_client

supabase = get_supabase_client()

class SurveyCreate(BaseModel):
    """
    Data model for creating a new survey.
    """
    user_id: str = Field(..., description="Email of the user taking the survey")
    physical: int = Field(..., description="Physical wellness score (0-100)", ge=0, le=100)
    financial: int = Field(..., description="Financial wellness score (0-100)", ge=0, le=100)
    emotional: int = Field(..., description="Emotional wellness score (0-100)", ge=0, le=100)
    spiritual: int = Field(..., description="Spiritual wellness score (0-100)", ge=0, le=100)
    social: int = Field(..., description="Social wellness score (0-100)", ge=0, le=100)
    environmental: int = Field(..., description="Environmental wellness score (0-100)", ge=0, le=100)
    creative: int = Field(..., description="Creative wellness score (0-100)", ge=0, le=100)


class SurveyResponse(BaseModel):
    """
    Data model for survey response.
    """
    survey_id: int
    user_id: str
    physical: int
    financial: int
    emotional: int
    spiritual: int
    social: int
    environmental: int
    creative: int
    created_at: Optional[date] = None


class SurveyUpdate(BaseModel):
    """
    Data model for updating a survey.
    """
    physical: Optional[int] = Field(None, description="Physical wellness score (0-100)", ge=0, le=100)
    financial: Optional[int] = Field(None, description="Financial wellness score (0-100)", ge=0, le=100)
    emotional: Optional[int] = Field(None, description="Emotional wellness score (0-100)", ge=0, le=100)
    spiritual: Optional[int] = Field(None, description="Spiritual wellness score (0-100)", ge=0, le=100)
    social: Optional[int] = Field(None, description="Social wellness score (0-100)", ge=0, le=100)
    environmental: Optional[int] = Field(None, description="Environmental wellness score (0-100)", ge=0, le=100)
    creative: Optional[int] = Field(None, description="Creative wellness score (0-100)", ge=0, le=100)


class SurveyStatsResponse(BaseModel):
    """
    Data model for survey statistics response.
    """
    average_physical: float
    average_financial: float
    average_emotional: float
    average_spiritual: float
    average_social: float
    average_environmental: float
    average_creative: float
    survey_count: int