"""
Resource service module.
This module contains the business logic for resource operations.
"""
from fastapi import HTTPException
from supabase import Client

from app.api.resources.model import ResourceCreate, ResourceUpdate

class ResourceService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "Resources"

    async def create_resource(self, resource: ResourceCreate):
        """
        Create a new resource in the database.
        
        Args:
            resource (ResourceCreate): Resource data
            
        Returns:
            dict: Created resource data
            
        Raises:
            HTTPException: If resource creation fails
        """
        try:
            # Insert resource into database
            result = self.supabase.table(self.table).insert(resource.dict()).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create resource")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating resource: {str(e)}")

    async def get_resource(self, type: str):
        """
        Get a resource by type.
        
        Args:
            type (str): Resource type
            
        Returns:
            dict: Resource data
            
        Raises:
            HTTPException: If resource is not found
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("type", type).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Resource with type {type} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving resource: {str(e)}")

    async def get_resources(self, limit: int = 100, offset: int = 0):
        """
        Get a list of resources with pagination.
        
        Args:
            limit (int, optional): Maximum number of resources to return. Defaults to 100.
            offset (int, optional): Number of resources to skip. Defaults to 0.
            
        Returns:
            list: List of resources
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table(self.table).select("*").range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving resources: {str(e)}")

    async def update_resource(self, type: str, resource: ResourceUpdate):
        """
        Update a resource by type.
        
        Args:
            type (str): Resource type
            resource (ResourceUpdate): Updated resource data
            
        Returns:
            dict: Updated resource data
            
        Raises:
            HTTPException: If resource update fails
        """
        try:
            # Filter out None values
            update_data = {k: v for k, v in resource.dict().items() if v is not None}
            
            # Update resource in database
            result = self.supabase.table(self.table).update(update_data).eq("type", type).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Resource with type {type} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating resource: {str(e)}")

    async def delete_resource(self, type: str):
        """
        Delete a resource by type.
        
        Args:
            type (str): Resource type
            
        Returns:
            dict: Deleted resource data
            
        Raises:
            HTTPException: If resource deletion fails
        """
        try:
            result = self.supabase.table(self.table).delete().eq("type", type).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Resource with type {type} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting resource: {str(e)}")
        