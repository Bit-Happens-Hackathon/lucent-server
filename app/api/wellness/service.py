"""
User wellness service module.
This module contains the business logic for user wellness operations.
"""
from fastapi import HTTPException
from supabase import Client
from datetime import date
from typing import List, Dict, Any, Optional

from app.api.wellness.model import UserWellnessCreate, UserWellnessUpdate

class UserWellnessService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "User_Wellness"

    async def create_user_wellness(self, wellness: UserWellnessCreate) -> Dict[str, Any]:
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
            # Validate that user exists first
            user_result = self.supabase.table("User").select("Email").eq("Email", wellness.user_id).execute()
            if not user_result.data:
                raise HTTPException(status_code=404, detail=f"User with email {wellness.user_id} not found")
            
            # Prepare data for insertion
            wellness_dict = {
                "User_id": wellness.user_id,
                "Physical": wellness.physical,
                "Financial": wellness.financial,
                "Emotional": wellness.emotional,
                "Spiritual": wellness.spiritual,
                "Social": wellness.social,
                "Environmental": wellness.environmental,
                "Creative": wellness.creative
            }
            
            # Add date if provided
            if wellness.date:
                wellness_dict["Date"] = str(wellness.date)
            
            # Insert wellness record into database
            result = self.supabase.table(self.table).insert(wellness_dict).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create wellness record")
                
            # Transform database result to match model format
            db_result = result.data[0]
            return {
                "wellness_id": db_result["Wellness_id"],
                "user_id": db_result["User_id"],
                "date": db_result["Date"],
                "physical": db_result["Physical"],
                "financial": db_result["Financial"],
                "emotional": db_result["Emotional"],
                "spiritual": db_result["Spiritual"],
                "social": db_result["Social"],
                "environmental": db_result["Environmental"],
                "creative": db_result["Creative"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating wellness record: {str(e)}")

    async def get_user_wellness(self, wellness_id: int) -> Dict[str, Any]:
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
            result = self.supabase.table(self.table).select("*").eq("Wellness_id", wellness_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
            
            # Transform database result to match model format
            db_result = result.data[0]
            return {
                "wellness_id": db_result["Wellness_id"],
                "user_id": db_result["User_id"],
                "date": db_result["Date"],
                "physical": db_result["Physical"],
                "financial": db_result["Financial"],
                "emotional": db_result["Emotional"],
                "spiritual": db_result["Spiritual"],
                "social": db_result["Social"],
                "environmental": db_result["Environmental"],
                "creative": db_result["Creative"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving wellness record: {str(e)}")

    async def get_user_wellness_records(
        self, 
        user_id: str, 
        limit: int = 100, 
        offset: int = 0,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get wellness records for a specific user with pagination.
        
        Args:
            user_id (str): User ID (email)
            limit (int, optional): Maximum number of records to return. Defaults to 100.
            offset (int, optional): Number of records to skip. Defaults to 0.
            start_date (date, optional): Start date for filtering records.
            end_date (date, optional): End date for filtering records.
            
        Returns:
            list: List of wellness records
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            # Build query
            query = self.supabase.table(self.table).select("*").eq("User_id", user_id)
            
            # Apply date filters if provided
            if start_date:
                query = query.gte("Date", str(start_date))
            if end_date:
                query = query.lte("Date", str(end_date))
                
            # Apply pagination and execute
            result = query.order("Date", desc=True).range(offset, offset + limit - 1).execute()
            
            # Transform database results to match model format
            transformed_data = []
            for record in result.data:
                transformed_data.append({
                    "wellness_id": record["Wellness_id"],
                    "user_id": record["User_id"],
                    "date": record["Date"],
                    "physical": record["Physical"],
                    "financial": record["Financial"],
                    "emotional": record["Emotional"],
                    "spiritual": record["Spiritual"],
                    "social": record["Social"],
                    "environmental": record["Environmental"],
                    "creative": record["Creative"]
                })
            
            return transformed_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving wellness records: {str(e)}")

    async def update_user_wellness(self, wellness_id: int, wellness: UserWellnessUpdate) -> Dict[str, Any]:
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
            
            if not update_data:
                # Return current wellness record if no updates provided
                return await self.get_user_wellness(wellness_id)
            
            # Map model fields to database columns
            field_mapping = {
                "date": "Date",
                "physical": "Physical",
                "financial": "Financial",
                "emotional": "Emotional",
                "spiritual": "Spiritual",
                "social": "Social",
                "environmental": "Environmental",
                "creative": "Creative"
            }
            
            db_update_data = {field_mapping.get(k, k): v for k, v in update_data.items()}
            
            # Convert date to string if present
            if "Date" in db_update_data and isinstance(db_update_data["Date"], date):
                db_update_data["Date"] = str(db_update_data["Date"])
            
            # Update wellness record in database
            result = self.supabase.table(self.table).update(db_update_data).eq("Wellness_id", wellness_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
                
            # Transform database result to match model format
            db_result = result.data[0]
            return {
                "wellness_id": db_result["Wellness_id"],
                "user_id": db_result["User_id"],
                "date": db_result["Date"],
                "physical": db_result["Physical"],
                "financial": db_result["Financial"],
                "emotional": db_result["Emotional"],
                "spiritual": db_result["Spiritual"],
                "social": db_result["Social"],
                "environmental": db_result["Environmental"],
                "creative": db_result["Creative"]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating wellness record: {str(e)}")

    async def delete_user_wellness(self, wellness_id: int) -> Dict[str, Any]:
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
            # Get record before deletion to return it
            wellness_data = await self.get_user_wellness(wellness_id)
            
            # Delete wellness record from database
            result = self.supabase.table(self.table).delete().eq("Wellness_id", wellness_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
                
            return wellness_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting wellness record: {str(e)}")