"""
User routes module.
This module defines the API endpoints for user operations.
"""
from fastapi import APIRouter, Depends, Query
from typing import List

from app.database import get_supabase_client
from app.api.users.service import UserService, UserCreate, UserUpdate
from app.api.users.model import UserCreate, UserResponse
# Create router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


# Dependency for UserService
def get_user_service():
    """
    Dependency for UserService.
    
    Returns:
        UserService: User service instance
    """
    return UserService(get_supabase_client())


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Create a new user.
    
    Args:
        user (UserCreate): User data
        user_service (UserService): User service instance
        
    Returns:
        UserResponse: Created user data
    """
    return await user_service.create_user(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Get a user by ID.
    
    Args:
        user_id (str): User ID
        user_service (UserService): User service instance
        
    Returns:
        UserResponse: User data
    """
    return await user_service.get_user(user_id)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get a list of users with pagination.
    
    Args:
        limit (int, optional): Maximum number of users to return. Defaults to 100.
        offset (int, optional): Number of users to skip. Defaults to 0.
        user_service (UserService): User service instance
        
    Returns:
        List[UserResponse]: List of users
    """
    return await user_service.get_users(limit, offset)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Update a user by ID.
    
    Args:
        user_id (str): User ID
        user (UserUpdate): Updated user data
        user_service (UserService): User service instance
        
    Returns:
        UserResponse: Updated user data
    """
    return await user_service.update_user(user_id, user)


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete a user by ID.
    
    Args:
        user_id (str): User ID
        user_service (UserService): User service instance
        
    Returns:
        UserResponse: Deleted user data
    """
    return await user_service.delete_user(user_id)