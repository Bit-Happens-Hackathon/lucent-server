"""
Survey routes module.
This module defines the API endpoints for survey operations.
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import date

from app.database import get_supabase_client
from app.api.surveys.service import SurveyService
from app.api.surveys.model import SurveyCreate, SurveyResponse, SurveyStatsResponse

# Create router
router = APIRouter(
    prefix="/surveys",
    tags=["surveys"],
    responses={404: {"description": "Not found"}},
)

# Dependency for SurveyService
def get_survey_service():
    """
    Dependency for SurveyService.
    
    Returns:
        SurveyService: Survey service instance
    """
    return SurveyService(get_supabase_client())


@router.post("/", response_model=SurveyResponse, status_code=201)
async def create_survey(
    survey: SurveyCreate,
    survey_service: SurveyService = Depends(get_survey_service)
):
    """
    Create a new survey submission.
    
    Args:
        survey (SurveyCreate): Survey data
        survey_service (SurveyService): Survey service instance
        
    Returns:
        SurveyResponse: Created survey data
    """
    return await survey_service.create_survey(survey)


@router.get("/{survey_id}", response_model=SurveyResponse)
async def get_survey(
    survey_id: int,
    survey_service: SurveyService = Depends(get_survey_service)
):
    """
    Get a survey by ID.
    
    Args:
        survey_id (int): Survey ID
        survey_service (SurveyService): Survey service instance
        
    Returns:
        SurveyResponse: Survey data
    """
    return await survey_service.get_survey(survey_id)


@router.get("/user/{user_id}", response_model=List[SurveyResponse])
async def get_user_surveys(
    user_id: str,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    survey_service: SurveyService = Depends(get_survey_service)
):
    """
    Get all surveys submitted by a specific user with optional date filtering.
    
    Args:
        user_id (str): User ID (email)
        limit (int, optional): Maximum number of surveys to return. Defaults to 100.
        offset (int, optional): Number of surveys to skip. Defaults to 0.
        start_date (date, optional): Start date for filtering surveys.
        end_date (date, optional): End date for filtering surveys.
        survey_service (SurveyService): Survey service instance
        
    Returns:
        List[SurveyResponse]: List of surveys
    """
    return await survey_service.get_user_surveys(user_id, limit, offset, start_date, end_date)


@router.get("/stats/{user_id}", response_model=SurveyStatsResponse)
async def get_user_survey_stats(
    user_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    survey_service: SurveyService = Depends(get_survey_service)
):
    """
    Get statistics for a user's surveys with optional date filtering.
    
    Args:
        user_id (str): User ID (email)
        start_date (date, optional): Start date for filtering surveys.
        end_date (date, optional): End date for filtering surveys.
        survey_service (SurveyService): Survey service instance
        
    Returns:
        SurveyStatsResponse: Survey statistics
    """
    return await survey_service.get_user_survey_stats(user_id, start_date, end_date)


@router.delete("/{survey_id}", response_model=SurveyResponse)
async def delete_survey(
    survey_id: int,
    survey_service: SurveyService = Depends(get_survey_service)
):
    """
    Delete a survey by ID.
    
    Args:
        survey_id (int): Survey ID
        survey_service (SurveyService): Survey service instance
        
    Returns:
        SurveyResponse: Deleted survey data
    """
    return await survey_service.delete_survey(survey_id)