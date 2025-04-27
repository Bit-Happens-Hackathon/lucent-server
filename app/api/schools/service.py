"""
School service module.
This module contains the business logic for school operations.
"""
from fastapi import HTTPException
from supabase import Client

from app.api.schools.model import SchoolCreate, SchoolUpdate

class SchoolService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "School"

    async def create_school(self, school: SchoolCreate):
        """
        Create a new school in the database.
        
        Args:
            school (SchoolCreate): School data
            
        Returns:
            dict: Created school data
            
        Raises:
            HTTPException: If school creation fails
        """
        try:
            # Insert school into database
            result = self.supabase.table(self.table).insert(school.dict()).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create school")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating school: {str(e)}")

    async def get_school(self, name: str):
        """
        Get a school by name.
        
        Args:
            name (str): School name
            
        Returns:
            dict: School data
            
        Raises:
            HTTPException: If school is not found
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("name", name).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"School with name {name} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving school: {str(e)}")

    async def get_schools(self, limit: int = 100, offset: int = 0):
        """
        Get a list of schools with pagination.
        
        Args:
            limit (int, optional): Maximum number of schools to return. Defaults to 100.
            offset (int, optional): Number of schools to skip. Defaults to 0.
            
        Returns:
            list: List of schools
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table(self.table).select("*").range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving schools: {str(e)}")

    async def update_school(self, name: str, school: SchoolUpdate):
        """
        Update a school by name.
        
        Args:
            name (str): School name
            school (SchoolUpdate): Updated school data
            
        Returns:
            dict: Updated school data
            
        Raises:
            HTTPException: If school update fails
        """
        try:
            # Filter out None values
            update_data = {k: v for k, v in school.dict().items() if v is not None}
            
            # Update school in database
            result = self.supabase.table(self.table).update(update_data).eq("name", name).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"School with name {name} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating school: {str(e)}")

    async def delete_school(self, name: str):
        """
        Delete a school by name.
        
        Args:
            name (str): School name
            
        Returns:
            dict: Deleted school data
            
        Raises:
            HTTPException: If school deletion fails
        """
        try:
            result = self.supabase.table(self.table).delete().eq("name", name).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"School with name {name} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting school: {str(e)}")
    
    # Relationship management methods
    async def add_resource_to_school(self, school_id: str, resource_id: str):
        """
        Add a resource to a school.
        
        Args:
            school_id (str): School name
            resource_id (str): Resource type
            
        Returns:
            dict: Created school resource association
            
        Raises:
            HTTPException: If operation fails
        """
        try:
            # First check if school exists
            school_result = self.supabase.table(self.table).select("*").eq("name", school_id).execute()
            
            if not school_result.data:
                raise HTTPException(status_code=404, detail=f"School with name {school_id} not found")
            
            # Then check if resource exists
            resource_result = self.supabase.table("Resources").select("*").eq("type", resource_id).execute()
            
            if not resource_result.data:
                raise HTTPException(status_code=404, detail=f"Resource with type {resource_id} not found")
            
            # Create the association
            data = {"school_id": school_id, "resource_id": resource_id}
            result = self.supabase.table(self.junction_table).insert(data).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to add resource to school")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding resource to school: {str(e)}")
    
    async def remove_resource_from_school(self, school_id: str, resource_id: str):
        """
        Remove a resource from a school.
        
        Args:
            school_id (str): School name
            resource_id (str): Resource type
            
        Returns:
            dict: Deleted school resource association
            
        Raises:
            HTTPException: If operation fails
        """
        try:
            result = self.supabase.table(self.junction_table).delete().eq("school_id", school_id).eq("resource_id", resource_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found for school {school_id}")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error removing resource from school: {str(e)}")
    
    async def get_school_resources(self, school_id: str):
        """
        Get all resources for a school.
        
        Args:
            school_id (str): School name
            
        Returns:
            list: List of resources
            
        Raises:
            HTTPException: If operation fails
        """
        try:
            # First check if school exists
            school_result = self.supabase.table(self.table).select("*").eq("name", school_id).execute()
            
            if not school_result.data:
                raise HTTPException(status_code=404, detail=f"School with name {school_id} not found")
            
            # Get all resources for this school using a join
            # Note: The actual approach depends on Supabase's join capabilities
            # This is a simplified example
            result = self.supabase.table(self.junction_table).select("resource_id").eq("school_id", school_id).execute()
            
            if not result.data:
                return []
            
            # Extract resource IDs
            resource_ids = [item["resource_id"] for item in result.data]
            
            # Get the actual resource details
            resources = []
            for resource_id in resource_ids:
                resource_result = self.supabase.table("Resources").select("*").eq("type", resource_id).execute()
                if resource_result.data:
                    resources.append(resource_result.data[0])
            
            return resources
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving resources for school: {str(e)}")
        
    # get school resource by type which is also ID
    async def get_school_resource_by_type(self, school_id: str, resource_id: str):
        """
        Get a specific resource for a school by type. The types are
        Physical, financial, emotional, spiritual, social, environmental, creative.

        Args:
            school_id (str): School name
            resource_id (str): Resource type
        Returns:
            dict: Resource data
        Raises:
            HTTPException: If operation fails
        """
        try:
            # First check if school exists
            school_result = self.supabase.table(self.table).select("*").eq("name", school_id).execute()
            
            if not school_result.data:
                raise HTTPException(status_code=404, detail=f"School with name {school_id} not found")
            
            # Then check if resource exists
            resource_result = self.supabase.table("Resources").select("*").eq("type", resource_id).execute()
            
            if not resource_result.data:
                raise HTTPException(status_code=404, detail=f"Resource with type {resource_id} not found")
            
            # Get the association
            result = self.supabase.table(self.junction_table).select("*").eq("school_id", school_id).eq("resource_id", resource_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found for school {school_id}")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving resource for school: {str(e)}")
        