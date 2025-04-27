"""
Activity routes module.
This module defines the API endpoints for user activity operations.
"""
from fastapi import APIRouter, Depends, Query
from typing import List

from app.database import get_supabase_client
from app.api.activity.service import ActivityService
from app.api.activity.model import ActivityCreate, ActivityResponse, ActivityUpdate

# Create router
router = APIRouter(
    prefix="/activity",
    tags=["activity"],
    responses={404: {"description": "Not found"}},
)

# Dependency for ActivityService
def get_activity_service():
    """
    Dependency for ActivityService.
    
    Returns:
        ActivityService: Activity service instance
    """
    return ActivityService(get_supabase_client())


@router.post("/", response_model=ActivityResponse, status_code=201)
async def create_activity(
    activity: ActivityCreate,
    activity_service: ActivityService = Depends(get_activity_service)
):
    """
    Create a new activity record.
    
    Args:
        activity (ActivityCreate): Activity data
        activity_service (ActivityService): Activity service instance
        
    Returns:
        ActivityResponse: Created activity data
    """
    return await activity_service.create_activity(activity)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: int,
    activity_service: ActivityService = Depends(get_activity_service)
):
    """
    Get an activity by ID.
    
    Args:
        activity_id (int): Activity ID
        activity_service (ActivityService): Activity service instance
        
    Returns:
        ActivityResponse: Activity data
    """
    return await activity_service.get_activity(activity_id)


@router.get("/", response_model=List[ActivityResponse])
async def get_activities(
    limit: int = Query(100, ge=1, le=365),
    offset: int = Query(0, ge=0),
    activity_service: ActivityService = Depends(get_activity_service)
):
    """
    Get a list of activities with pagination.
    
    Args:
        limit (int, optional): Maximum number of activities to return. Defaults to 100.
        offset (int, optional): Number of activities to skip. Defaults to 0.
        activity_service (ActivityService): Activity service instance
        
    Returns:
        List[ActivityResponse]: List of activities
    """
    return await activity_service.get_activities(limit, offset)


@router.get("/user/{user_id}", response_model=List[ActivityResponse])
async def get_user_activities(
    user_id: str,
    limit: int = Query(100, ge=1, le=365),
    offset: int = Query(0, ge=0),
    activity_service: ActivityService = Depends(get_activity_service)
):
    """
    Get activities for a specific user with pagination.
    
    Args:
        user_id (str): User ID (email)
        limit (int, optional): Maximum number of activities to return. Defaults to 100.
        offset (int, optional): Number of activities to skip. Defaults to 0.
        activity_service (ActivityService): Activity service instance
        
    Returns:
        List[ActivityResponse]: List of user activities
    """
    return await activity_service.get_user_activities(user_id, limit, offset)


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity: ActivityUpdate,
    activity_service: ActivityService = Depends(get_activity_service)
):
    """
    Update an activity by ID.
    
    Args:
        activity_id (int): Activity ID
        activity (ActivityUpdate): Updated activity data
        activity_service (ActivityService): Activity service instance
        
    Returns:
        ActivityResponse: Updated activity data
    """
    return await activity_service.update_activity(activity_id, activity)


@router.delete("/{activity_id}", response_model=ActivityResponse)
async def delete_activity(
    activity_id: int,
    activity_service: ActivityService = Depends(get_activity_service)
):
    """
    Delete an activity by ID.
    
    Args:
        activity_id (int): Activity ID
        activity_service (ActivityService): Activity service instance
        
    Returns:
        ActivityResponse: Deleted activity data
    """
    return await activity_service.delete_activity(activity_id)