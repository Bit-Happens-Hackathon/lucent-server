"""
Survey service module.
This module contains the business logic for survey operations.
"""
from fastapi import HTTPException
from supabase import Client
from typing import List, Optional, Dict, Any
from datetime import date
from statistics import mean

from app.api.surveys.model import SurveyCreate, SurveyUpdate, SurveyStatsResponse

class SurveyService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "User_Wellness"

    async def create_survey(self, survey: SurveyCreate):
        """
        Create a new survey in the database.
        
        Args:
            survey (SurveyCreate): Survey data
            
        Returns:
            dict: Created survey data
            
        Raises:
            HTTPException: If survey creation fails
        """
        try:
            # Validate that user exists
            user_result = self.supabase.table("User").select("Email").eq("Email", survey.user_id).execute()
            if not user_result.data:
                raise HTTPException(status_code=404, detail=f"User with email {survey.user_id} not found")
            
            # Insert survey into database
            survey_dict = survey.dict()
            
            result = self.supabase.table(self.table).insert(survey_dict).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create survey")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating survey: {str(e)}")

    async def get_survey(self, survey_id: int):
        """
        Get a survey by ID.
        
        Args:
            survey_id (int): Survey ID
            
        Returns:
            dict: Survey data
            
        Raises:
            HTTPException: If survey is not found
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("Wellness_id", survey_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
                
            # Transform the data to match the response model
            survey_data = result.data[0]
            return {
                "survey_id": survey_data["Wellness_id"],
                "user_id": survey_data["User_id"],
                "physical": survey_data["Physical"],
                "financial": survey_data["Financial"],
                "emotional": survey_data["Emotional"],
                "spiritual": survey_data["Spiritual"],
                "social": survey_data["Social"],
                "environmental": survey_data["Environmental"],
                "creative": survey_data["Creative"],
                "date": survey_data.get("Date")
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving survey: {str(e)}")

    async def get_user_surveys(
        self, 
        user_id: str, 
        limit: int = 100, 
        offset: int = 0,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all surveys for a specific user with optional date filtering.
        
        Args:
            user_id (str): User ID (email)
            limit (int, optional): Maximum number of surveys to return. Defaults to 100.
            offset (int, optional): Number of surveys to skip. Defaults to 0.
            start_date (date, optional): Start date for filtering surveys.
            end_date (date, optional): End date for filtering surveys.
            
        Returns:
            List[Dict[str, Any]]: List of surveys
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            # Verify user exists
            user_result = self.supabase.table("User").select("Email").eq("Email", user_id).execute()
            if not user_result.data:
                raise HTTPException(status_code=404, detail=f"User with email {user_id} not found")
                
            # Build query
            query = self.supabase.table(self.table).select("*").eq("User_id", user_id)
            
            # Apply date filters if provided
            if start_date:
                query = query.gte("Date", str(start_date))
            if end_date:
                query = query.lte("Date", str(end_date))
                
            # Apply pagination and execute
            result = query.order("Date", desc=True).range(offset, offset + limit - 1).execute()
            
            # Transform the data to match the response model
            transformed_data = []
            for survey in result.data:
                transformed_data.append({
                    "survey_id": survey["Wellness_id"],
                    "user_id": survey["User_id"],
                    "physical": survey["Physical"],
                    "financial": survey["Financial"],
                    "emotional": survey["Emotional"],
                    "spiritual": survey["Spiritual"],
                    "social": survey["Social"],
                    "environmental": survey["Environmental"],
                    "creative": survey["Creative"],
                    "date": survey.get("Date")
                })
            
            return transformed_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving user surveys: {str(e)}")

    async def get_user_survey_stats(
        self, 
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> SurveyStatsResponse:
        """
        Get statistics for a user's surveys with optional date filtering.
        
        Args:
            user_id (str): User ID (email)
            start_date (date, optional): Start date for filtering surveys.
            end_date (date, optional): End date for filtering surveys.
            
        Returns:
            SurveyStatsResponse: Survey statistics
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            # Get all user surveys within the date range
            surveys = await self.get_user_surveys(
                user_id=user_id, 
                limit=1000,  # Large limit to get all surveys
                start_date=start_date,
                end_date=end_date
            )
            
            if not surveys:
                return SurveyStatsResponse(
                    average_physical=0,
                    average_financial=0,
                    average_emotional=0,
                    average_spiritual=0,
                    average_social=0,
                    average_environmental=0,
                    average_creative=0,
                    survey_count=0
                )
            
            # Calculate averages
            return SurveyStatsResponse(
                average_physical=mean([s["physical"] for s in surveys]),
                average_financial=mean([s["financial"] for s in surveys]),
                average_emotional=mean([s["emotional"] for s in surveys]),
                average_spiritual=mean([s["spiritual"] for s in surveys]),
                average_social=mean([s["social"] for s in surveys]),
                average_environmental=mean([s["environmental"] for s in surveys]),
                average_creative=mean([s["creative"] for s in surveys]),
                survey_count=len(surveys)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calculating survey statistics: {str(e)}")

    async def update_survey(self, survey_id: int, survey: SurveyUpdate):
        """
        Update a survey by ID.
        
        Args:
            survey_id (int): Survey ID
            survey (SurveyUpdate): Updated survey data
            
        Returns:
            dict: Updated survey data
            
        Raises:
            HTTPException: If survey update fails
        """
        try:
            # Filter out None values
            update_data = {k: v for k, v in survey.dict().items() if v is not None}
            
            if not update_data:
                # Return current survey if no updates provided
                return await self.get_survey(survey_id)
            
            # Map field names to match database column names if necessary
            field_mapping = {
                "physical": "Physical",
                "financial": "Financial",
                "emotional": "Emotional",
                "spiritual": "Spiritual",
                "social": "Social",
                "environmental": "Environmental",
                "creative": "Creative"
            }
            
            db_update_data = {field_mapping.get(k, k): v for k, v in update_data.items()}
            
            # Update survey in database
            result = self.supabase.table(self.table).update(db_update_data).eq("Wellness_id", survey_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
                
            # Transform the data to match the response model
            survey_data = result.data[0]
            return {
                "survey_id": survey_data["Wellness_id"],
                "user_id": survey_data["User_id"],
                "physical": survey_data["Physical"],
                "financial": survey_data["Financial"],
                "emotional": survey_data["Emotional"],
                "spiritual": survey_data["Spiritual"],
                "social": survey_data["Social"],
                "environmental": survey_data["Environmental"],
                "creative": survey_data["Creative"],
                "date": survey_data.get("Date")
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating survey: {str(e)}")

    async def delete_survey(self, survey_id: int):
        """
        Delete a survey by ID.
        
        Args:
            survey_id (int): Survey ID
            
        Returns:
            dict: Deleted survey data
            
        Raises:
            HTTPException: If survey deletion fails
        """
        try:
            # Get survey data before deletion for return
            survey = await self.get_survey(survey_id)
            
            # Delete survey from database
            result = self.supabase.table(self.table).delete().eq("Wellness_id", survey_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Survey with ID {survey_id} not found")
                
            return survey
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting survey: {str(e)}")