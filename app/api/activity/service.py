"""
Activity service module.
This module contains the business logic for user activity operations.
"""
from fastapi import HTTPException
from supabase import Client
from datetime import datetime

from app.api.activity.model import ActivityCreate, ActivityUpdate

class ActivityService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "User_Activity"

    async def create_activity(self, activity: ActivityCreate):
        """
        Create a new activity record in the database.
        
        Args:
            activity (ActivityCreate): Activity data
            
        Returns:
            dict: Created activity data
            
        Raises:
            HTTPException: If activity creation fails
        """
        try:
            # Convert datetime to string for Supabase
            activity_dict = activity.model_dump()
            if activity_dict.get("login"):
                activity_dict["login"] = activity_dict["login"].isoformat()
            
            # Insert activity into database
            result = self.supabase.table(self.table).insert(activity_dict).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create activity record")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating activity record: {str(e)}")

    async def get_activity(self, activity_id: int):
        """
        Get an activity by ID.
        
        Args:
            activity_id (int): Activity ID
            
        Returns:
            dict: Activity data
            
        Raises:
            HTTPException: If activity is not found
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("activity_id", activity_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Activity with ID {activity_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving activity: {str(e)}")

    async def get_activities(self, limit: int = 100, offset: int = 0):
        """
        Get a list of activities with pagination.
        
        Args:
            limit (int, optional): Maximum number of activities to return. Defaults to 100.
            offset (int, optional): Number of activities to skip. Defaults to 0.
            
        Returns:
            list: List of activities
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table(self.table).select("*").range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving activities: {str(e)}")

    async def get_user_activities(self, user_id: str, limit: int = 365, offset: int = 0):
        """
        Get login dates for a specific user with pagination.
        
        Args:
            user_id (str): User ID (email)
            limit (int, optional): Maximum number of activities to return. Defaults to 365.
            offset (int, optional): Number of activities to skip. Defaults to 0.
            
        Returns:
            list: List of activity objects with login dates
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("user_id", user_id).range(offset, offset + limit - 1).execute()
            
            # Return the full activity objects instead of just the login field
            # This ensures we match the expected response model structure
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving user activities: {str(e)}")

    async def update_activity(self, activity_id: int, activity: ActivityUpdate):
        """
        Update an activity by ID.
        
        Args:
            activity_id (int): Activity ID
            activity (ActivityUpdate): Updated activity data
            
        Returns:
            dict: Updated activity data
            
        Raises:
            HTTPException: If activity update fails
        """
        try:
            # Filter out None values
            update_data = {k: v for k, v in activity.dict().items() if v is not None}
            
            # Convert datetime to string if present
            if "login" in update_data and isinstance(update_data["login"], datetime):
                update_data["login"] = update_data["login"].isoformat()
            
            # Update activity in database
            result = self.supabase.table(self.table).update(update_data).eq("activity_id", activity_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Activity with ID {activity_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating activity: {str(e)}")

    async def delete_activity(self, activity_id: int):
        """
        Delete an activity by ID.
        
        Args:
            activity_id (int): Activity ID
            
        Returns:
            dict: Deleted activity data
            
        Raises:
            HTTPException: If activity deletion fails
        """
        try:
            result = self.supabase.table(self.table).delete().eq("activity_id", activity_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Activity with ID {activity_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting activity: {str(e)}")