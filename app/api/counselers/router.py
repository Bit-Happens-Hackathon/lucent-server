"""
Counselor routes module.
This module defines the API endpoints for counselor operations.
"""
from fastapi import APIRouter, Depends, Query
from typing import List
from app.database import get_supabase_client
from app.api.counselers.service import CounselorService
from app.api.counselers.model import CounselorCreate, CounselorResponse, CounselorUpdate

# Create router
router = APIRouter(
    prefix="/counselors",
    tags=["counselors"],
    responses={404: {"description": "Not found"}},
)

# Dependency for CounselorService
def get_counselor_service():
    """
    Dependency for CounselorService.
    
    Returns:
        CounselorService: Counselor service instance
    """
    return CounselorService(get_supabase_client())

@router.post("/", response_model=CounselorResponse, status_code=201)
async def create_counselor(
    counselor: CounselorCreate,
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    Create a new counselor.
    
    Args:
        counselor (CounselorCreate): Counselor data
        counselor_service (CounselorService): Counselor service instance
        
    Returns:
        CounselorResponse: Created counselor data
    """
    return await counselor_service.create_counselor(counselor)

@router.get("/{counselor_id}", response_model=CounselorResponse)
async def get_counselor(
    counselor_id: int,
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    Get a counselor by ID.
    
    Args:
        counselor_id (int): Counselor ID
        counselor_service (CounselorService): Counselor service instance
        
    Returns:
        CounselorResponse: Counselor data
    """
    return await counselor_service.get_counselor(counselor_id)

@router.get("/email/{email}", response_model=CounselorResponse)
async def get_counselor_by_email(
    email: str,
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    Get a counselor by email.
    
    Args:
        email (str): Counselor email
        counselor_service (CounselorService): Counselor service instance
        
    Returns:
        CounselorResponse: Counselor data
    """
    return await counselor_service.get_counselor_by_email(email)

@router.get("/", response_model=List[CounselorResponse])
async def get_counselors(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    Get a list of counselors with pagination.
    
    Args:
        limit (int, optional): Maximum number of counselors to return. Defaults to 100.
        offset (int, optional): Number of counselors to skip. Defaults to 0.
        counselor_service (CounselorService): Counselor service instance
        
    Returns:
        List[CounselorResponse]: List of counselors
    """
    return await counselor_service.get_counselors(limit, offset)

@router.get("/school/{school_id}", response_model=List[CounselorResponse])
async def get_counselors_by_school(
    school_id: str,
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    Get counselors by school.
    
    Args:
        school_id (str): School name
        counselor_service (CounselorService): Counselor service instance
        
    Returns:
        List[CounselorResponse]: List of counselors
    """
    return await counselor_service.get_counselors_by_school(school_id)

@router.put("/{counselor_id}", response_model=CounselorResponse)
async def update_counselor(
    counselor_id: int,
    counselor: CounselorUpdate,
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    Update a counselor by ID.
    
    Args:
        counselor_id (int): Counselor ID
        counselor (CounselorUpdate): Updated counselor data
        counselor_service (CounselorService): Counselor service instance
        
    Returns:
        CounselorResponse: Updated counselor data
    """
    return await counselor_service.update_counselor(counselor_id, counselor)

@router.delete("/{counselor_id}", response_model=CounselorResponse)
async def delete_counselor(
    counselor_id: int,
    counselor_service: CounselorService = Depends(get_counselor_service)
):
    """
    Delete a counselor by ID.
    
    Args:
        counselor_id (int): Counselor ID
        counselor_service (CounselorService): Counselor service instance
        
    Returns:
        CounselorResponse: Deleted counselor data
    """
    return await counselor_service.delete_counselor(counselor_id)