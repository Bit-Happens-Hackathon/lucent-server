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