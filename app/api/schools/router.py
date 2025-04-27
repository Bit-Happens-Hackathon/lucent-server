"""
School routes module.
This module defines the API endpoints for school operations.
"""
from fastapi import APIRouter, Depends, Query
from typing import List
from app.database import get_supabase_client
from app.api.schools.service import SchoolService
from app.api.schools.model import SchoolCreate, SchoolResponse, SchoolUpdate

# Create router
router = APIRouter(
    prefix="/schools",
    tags=["schools"],
    responses={404: {"description": "Not found"}},
)

# Dependency for SchoolService
def get_school_service():
    """
    Dependency for SchoolService.
    
    Returns:
        SchoolService: School service instance
    """
    return SchoolService(get_supabase_client())

@router.post("/", response_model=SchoolResponse, status_code=201)
async def create_school(
    school: SchoolCreate,
    school_service: SchoolService = Depends(get_school_service)
):
    """
    Create a new school.
    
    Args:
        school (SchoolCreate): School data
        school_service (SchoolService): School service instance
        
    Returns:
        SchoolResponse: Created school data
    """
    return await school_service.create_school(school)

@router.get("/{name}", response_model=SchoolResponse)
async def get_school(
    name: str,
    school_service: SchoolService = Depends(get_school_service)
):
    """
    Get a school by name.
    
    Args:
        name (str): School name
        school_service (SchoolService): School service instance
        
    Returns:
        SchoolResponse: School data
    """
    return await school_service.get_school(name)

@router.get("/", response_model=List[SchoolResponse])
async def get_schools(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    school_service: SchoolService = Depends(get_school_service)
):
    """
    Get a list of schools with pagination.
    
    Args:
        limit (int, optional): Maximum number of schools to return. Defaults to 100.
        offset (int, optional): Number of schools to skip. Defaults to 0.
        school_service (SchoolService): School service instance
        
    Returns:
        List[SchoolResponse]: List of schools
    """
    return await school_service.get_schools(limit, offset)

@router.put("/{name}", response_model=SchoolResponse)
async def update_school(
    name: str,
    school: SchoolUpdate,
    school_service: SchoolService = Depends(get_school_service)
):
    """
    Update a school by name.
    
    Args:
        name (str): School name
        school (SchoolUpdate): Updated school data
        school_service (SchoolService): School service instance
        
    Returns:
        SchoolResponse: Updated school data
    """
    return await school_service.update_school(name, school)

@router.delete("/{name}", response_model=SchoolResponse)
async def delete_school(
    name: str,
    school_service: SchoolService = Depends(get_school_service)
):
    """
    Delete a school by name.
    
    Args:
        name (str): School name
        school_service (SchoolService): School service instance
        
    Returns:
        SchoolResponse: Deleted school data
    """
    return await school_service.delete_school(name)