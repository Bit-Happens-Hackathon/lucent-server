"""
User wellness service module.
This module contains the business logic for user wellness operations.
"""
from fastapi import HTTPException
from supabase import Client
from datetime import date, datetime
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
            user_result = self.supabase.table("User").select("email").eq("email", wellness.user_id).execute()
            if not user_result.data:
                raise HTTPException(status_code=404, detail=f"User with email {wellness.user_id} not found")
            
            # Prepare data for insertion
            wellness_dict = {
                "user_id": wellness.user_id,
                "physical": wellness.physical,
                "financial": wellness.financial,
                "emotional": wellness.emotional,
                "spiritual": wellness.spiritual,
                "social": wellness.social,
                "environmental": wellness.environmental,
                "creative": wellness.creative,
                "date": datetime.now().isoformat()
            }
            
            
            # Insert wellness record into database
            result = self.supabase.table(self.table).insert(wellness_dict).execute()

                
            # Transform database result to match model format
            db_result = result.data[0]
            return {
                "wellness_id": db_result["wellness_id"],  # Changed from "Wellness_id" to "wellness_id"
                "user_id": db_result["user_id"],  # Changed from "User_id" to "user_id"
                "date": db_result["date"],  # Changed from "Date" to "date"
                "physical": db_result["physical"],  # Changed from "Physical" to "physical"
                "financial": db_result["financial"],  # Changed from "Financial" to "financial"
                "emotional": db_result["emotional"],  # Changed from "Emotional" to "emotional"
                "spiritual": db_result["spiritual"],  # Changed from "Spiritual" to "spiritual"
                "social": db_result["social"],  # Changed from "Social" to "social"
                "environmental": db_result["environmental"],  # Changed from "Environmental" to "environmental"
                "creative": db_result["creative"]  # Changed from "Creative" to "creative"
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
            result = self.supabase.table(self.table).select("*").eq("wellness_id", wellness_id).execute()  # Changed from "Wellness_id" to "wellness_id"
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
            
            # Transform database result to match model format
            db_result = result.data[0]
            return {
                "wellness_id": db_result["wellness_id"],  # Changed from "Wellness_id" to "wellness_id"
                "user_id": db_result["user_id"],  # Changed from "User_id" to "user_id"
                "date": db_result["date"],  # Changed from "Date" to "date"
                "physical": db_result["physical"],  # Changed from "Physical" to "physical"
                "financial": db_result["financial"],  # Changed from "Financial" to "financial"
                "emotional": db_result["emotional"],  # Changed from "Emotional" to "emotional"
                "spiritual": db_result["spiritual"],  # Changed from "Spiritual" to "spiritual"
                "social": db_result["social"],  # Changed from "Social" to "social"
                "environmental": db_result["environmental"],  # Changed from "Environmental" to "environmental"
                "creative": db_result["creative"]  # Changed from "Creative" to "creative"
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
            query = self.supabase.table(self.table).select("*").eq("user_id", user_id)  # Changed from "User_id" to "user_id"
            
            # Apply date filters if provided
            if start_date:
                query = query.gte("date", str(start_date))  # Changed from "Date" to "date"
            if end_date:
                query = query.lte("date", str(end_date))  # Changed from "Date" to "date"
                
            # Apply pagination and execute
            result = query.order("date", desc=True).range(offset, offset + limit - 1).execute()  # Changed from "Date" to "date"
            
            # Transform database results to match model format
            transformed_data = []
            for record in result.data:
                # Handle the date format conversion
                date_str = record["date"]
                # Check if the date contains a time component
                if "T" in date_str:
                    # Extract just the date portion (YYYY-MM-DD)
                    date_str = date_str.split("T")[0]
                
                transformed_data.append({
                    "wellness_id": record["wellness_id"],
                    "user_id": record["user_id"],
                    "date": date_str,  # Use the cleaned date string
                    "physical": record["physical"],
                    "financial": record["financial"],
                    "emotional": record["emotional"],
                    "spiritual": record["spiritual"],
                    "social": record["social"],
                    "environmental": record["environmental"],
                    "creative": record["creative"]
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
                "record_date": "date",  # Changed from "Date" to "date" and "date" to "record_date"
                "physical": "physical",  # Kept the same (lowercase)
                "financial": "financial",  # Kept the same (lowercase)
                "emotional": "emotional",  # Kept the same (lowercase)
                "spiritual": "spiritual",  # Kept the same (lowercase)
                "social": "social",  # Kept the same (lowercase)
                "environmental": "environmental",  # Kept the same (lowercase)
                "creative": "creative"  # Kept the same (lowercase)
            }
            
            db_update_data = {field_mapping.get(k, k): v for k, v in update_data.items()}
            
            # Convert date to string if present
            if "date" in db_update_data and isinstance(db_update_data["date"], date):  # Changed from "Date" to "date"
                db_update_data["date"] = str(db_update_data["date"])  # Changed from "Date" to "date"
            
            # Update wellness record in database
            result = self.supabase.table(self.table).update(db_update_data).eq("wellness_id", wellness_id).execute()  # Changed from "Wellness_id" to "wellness_id"
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
                
            # Transform database result to match model format
            db_result = result.data[0]
            return {
                "wellness_id": db_result["wellness_id"],  # Changed from "Wellness_id" to "wellness_id"
                "user_id": db_result["user_id"],  # Changed from "User_id" to "user_id"
                "date": db_result["date"],  # Changed from "Date" to "date"
                "physical": db_result["physical"],  # Changed from "Physical" to "physical"
                "financial": db_result["financial"],  # Changed from "Financial" to "financial"
                "emotional": db_result["emotional"],  # Changed from "Emotional" to "emotional"
                "spiritual": db_result["spiritual"],  # Changed from "Spiritual" to "spiritual"
                "social": db_result["social"],  # Changed from "Social" to "social"
                "environmental": db_result["environmental"],  # Changed from "Environmental" to "environmental"
                "creative": db_result["creative"]  # Changed from "Creative" to "creative"
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
            result = self.supabase.table(self.table).delete().eq("wellness_id", wellness_id).execute()  # Changed from "Wellness_id" to "wellness_id"
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Wellness record with ID {wellness_id} not found")
                
            return wellness_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting wellness record: {str(e)}")