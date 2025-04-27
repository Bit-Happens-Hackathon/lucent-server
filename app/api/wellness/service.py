"""
User wellness service module.
This module contains the business logic for user wellness operations.
"""
from fastapi import HTTPException
from supabase import Client
from datetime import date

from app.api.wellness.model import UserWellnessCreate, UserWellnessUpdate

class UserWellnessService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "User_Wellness"

    async def create_user_wellness(self, wellness: UserWellnessCreate):
        """
        Create a new user wellness record in the database.
        
        Args:
            wellness (UserWellnessCreate): User wellness data
            
        Returns:
            dict: Created user wellness data
            
        Raises:
            HTTPException: If wellness creation fails
        """
        try:
            wellness_dict = wellness.dict()
            
            # Convert date to string for Supabase if present
            if wellness.date:
                wellness_dict["date"] = str(wellness.date)
            
            # Insert wellness record into database
            result = self.supabase.table(self.table).insert(wellness_dict).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create wellness record")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating wellness record: {str(e)}")

    async def get_user_wellness(self, wellness_id: int):
        """
        Get a user wellness record by ID.
        
        Args:
            wellness_id (int): Wellness record ID
            
        Returns:
            dict: User wellness data
            
        Raises:
            HTTPException: If wellness record is not found
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("wellness_id", wellness_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving wellness record: {str(e)}")

    async def get_user_wellness_records(self, user_id: str, limit: int = 100, offset: int = 0):
        """
        Get wellness records for a specific user with pagination.
        
        Args:
            user_id (str): User ID (email)
            limit (int, optional): Maximum number of records to return. Defaults to 100.
            offset (int, optional): Number of records to skip. Defaults to 0.
            
        Returns:
            list: List of wellness records
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("user_id", user_id).order("date", desc=True).range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving wellness records: {str(e)}")

    async def update_user_wellness(self, wellness_id: int, wellness: UserWellnessUpdate):
        """
        Update a user wellness record by ID.
        
        Args:
            wellness_id (int): Wellness record ID
            wellness (UserWellnessUpdate): Updated wellness data
            
        Returns:
            dict: Updated wellness data
            
        Raises:
            HTTPException: If wellness update fails
        """
        try:
            # Filter out None values
            update_data = {k: v for k, v in wellness.dict().items() if v is not None}
            
            # Convert date to string if present
            if "date" in update_data and isinstance(update_data["date"], date):
                update_data["date"] = str(update_data["date"])
            
            # Update wellness record in database
            result = self.supabase.table(self.table).update(update_data).eq("wellness_id", wellness_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating wellness record: {str(e)}")

    async def delete_user_wellness(self, wellness_id: int):
        """
        Delete a user wellness record by ID.
        
        Args:
            wellness_id (int): Wellness record ID
            
        Returns:
            dict: Deleted wellness data
            
        Raises:
            HTTPException: If wellness deletion fails
        """
        try:
            result = self.supabase.table(self.table).delete().eq("wellness_id", wellness_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting wellness record: {str(e)}")