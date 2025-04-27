"""
User wellness routes module.
This module defines the API endpoints for user wellness operations.
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import date

from app.database import get_supabase_client
from app.api.wellness.model import UserWellnessCreate, UserWellnessResponse, UserWellnessUpdate
from app.api.wellness.service import UserWellnessService

# Create router
router = APIRouter(
    prefix="/wellness",
    tags=["wellness"],
    responses={404: {"description": "Not found"}},
)

# Dependency for UserWellnessService
def get_user_wellness_service():
    """
    Dependency for UserWellnessService.
    
    Returns:
        UserWellnessService: User wellness service instance
    """
    return UserWellnessService(get_supabase_client())

@router.post("/", response_model=UserWellnessResponse, status_code=201)
async def create_user_wellness(
    wellness: UserWellnessCreate,
    wellness_service: UserWellnessService = Depends(get_user_wellness_service)
):
    """
    Create a new user wellness record.
    
    Args:
        wellness (UserWellnessCreate): User wellness data
        wellness_service (UserWellnessService): User wellness service instance
        
    Returns:
        UserWellnessResponse: Created user wellness data
    """
    return await wellness_service.create_user_wellness(wellness)

@router.get("/{wellness_id}", response_model=UserWellnessResponse)
async def get_user_wellness(
    wellness_id: int,
    wellness_service: UserWellnessService = Depends(get_user_wellness_service)
):
    """
    Get a user wellness record by ID.
    
    Args:
        wellness_id (int): Wellness record ID
        wellness_service (UserWellnessService): User wellness service instance
        
    Returns:
        UserWellnessResponse: User wellness data
    """
    return await wellness_service.get_user_wellness(wellness_id)

@router.get("/user/{user_id}", response_model=List[UserWellnessResponse])
async def get_user_wellness_records(
    user_id: str,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    wellness_service: UserWellnessService = Depends(get_user_wellness_service)
):
    """
    Get wellness records for a specific user with pagination.
    
    Args:
        user_id (str): User ID (email)
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        offset (int, optional): Number of records to skip. Defaults to 0.
        start_date (date, optional): Start date for filtering records.
        end_date (date, optional): End date for filtering records.
        wellness_service (UserWellnessService): User wellness service instance
        
    Returns:
        List[UserWellnessResponse]: List of wellness records
    """
    return await wellness_service.get_user_wellness_records(
        user_id, 
        limit, 
        offset,
        start_date,
        end_date
    )

@router.put("/{wellness_id}", response_model=UserWellnessResponse)
async def update_user_wellness(
    wellness_id: int,
    wellness: UserWellnessUpdate,
    wellness_service: UserWellnessService = Depends(get_user_wellness_service)
):
    """
    Update a user wellness record by ID.
    
    Args:
        wellness_id (int): Wellness record ID
        wellness (UserWellnessUpdate): Updated wellness data
        wellness_service (UserWellnessService): User wellness service instance
        
    Returns:
        UserWellnessResponse: Updated user wellness data
    """
    return await wellness_service.update_user_wellness(wellness_id, wellness)

@router.delete("/{wellness_id}", response_model=UserWellnessResponse)
async def delete_user_wellness(
    wellness_id: int,
    wellness_service: UserWellnessService = Depends(get_user_wellness_service)
):
    """
    Delete a user wellness record by ID.
    
    Args:
        wellness_id (int): Wellness record ID
        wellness_service (UserWellnessService): User wellness service instance
        
    Returns:
        UserWellnessResponse: Deleted user wellness data
    """
    return await wellness_service.delete_user_wellness(wellness_id)