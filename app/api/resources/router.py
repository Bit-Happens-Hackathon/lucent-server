"""
Resource routes module.
This module defines the API endpoints for resource operations.
"""
from fastapi import APIRouter, Depends, Query
from typing import List
from app.database import get_supabase_client
from app.api.resources.service import ResourceService
from app.api.resources.model import ResourceCreate, ResourceResponse, ResourceUpdate

# Create router
router = APIRouter(
    prefix="/resources",
    tags=["resources"],
    responses={404: {"description": "Not found"}},
)

# Dependency for ResourceService
def get_resource_service():
    """
    Dependency for ResourceService.
    
    Returns:
        ResourceService: Resource service instance
    """
    return ResourceService(get_supabase_client())

@router.post("/", response_model=ResourceResponse, status_code=201)
async def create_resource(
    resource: ResourceCreate,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    Create a new resource.
    
    Args:
        resource (ResourceCreate): Resource data
        resource_service (ResourceService): Resource service instance
        
    Returns:
        ResourceResponse: Created resource data
    """
    return await resource_service.create_resource(resource)

@router.get("/{type}", response_model=ResourceResponse)
async def get_resource(
    type: str,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    Get a resource by type.
    
    Args:
        type (str): Resource type
        resource_service (ResourceService): Resource service instance
        
    Returns:
        ResourceResponse: Resource data
    """
    return await resource_service.get_resource(type)

@router.get("/", response_model=List[ResourceResponse])
async def get_resources(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    Get a list of resources with pagination.
    
    Args:
        limit (int, optional): Maximum number of resources to return. Defaults to 100.
        offset (int, optional): Number of resources to skip. Defaults to 0.
        resource_service (ResourceService): Resource service instance
        
    Returns:
        List[ResourceResponse]: List of resources
    """
    return await resource_service.get_resources(limit, offset)

@router.put("/{type}", response_model=ResourceResponse)
async def update_resource(
    type: str,
    resource: ResourceUpdate,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    Update a resource by type.
    
    Args:
        type (str): Resource type
        resource (ResourceUpdate): Updated resource data
        resource_service (ResourceService): Resource service instance
        
    Returns:
        ResourceResponse: Updated resource data
    """
    return await resource_service.update_resource(type, resource)

@router.delete("/{type}", response_model=ResourceResponse)
async def delete_resource(
    type: str,
    resource_service: ResourceService = Depends(get_resource_service)
):
    """
    Delete a resource by type.
    
    Args:
        type (str): Resource type
        resource_service (ResourceService): Resource service instance
        
    Returns:
        ResourceResponse: Deleted resource data
    """
    return await resource_service.delete_resource(type)