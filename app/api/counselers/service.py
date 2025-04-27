"""
Counselor service module.
This module contains the business logic for counselor operations.
"""
from fastapi import HTTPException
from supabase import Client

from app.api.counselers.model import CounselorCreate, CounselorUpdate

class CounselorService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "Counselors"

    async def create_counselor(self, counselor: CounselorCreate):
        """
        Create a new counselor in the database.
        
        Args:
            counselor (CounselorCreate): Counselor data
            
        Returns:
            dict: Created counselor data
            
        Raises:
            HTTPException: If counselor creation fails
        """
        try:
            # Insert counselor into database
            result = self.supabase.table(self.table).insert(counselor.dict()).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create counselor")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating counselor: {str(e)}")

    async def get_counselor(self, counselor_id: int):
        """
        Get a counselor by ID.
        
        Args:
            counselor_id (int): Counselor ID
            
        Returns:
            dict: Counselor data
            
        Raises:
            HTTPException: If counselor is not found
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("id", counselor_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Counselor with ID {counselor_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving counselor: {str(e)}")
    
    async def get_counselor_by_email(self, email: str):
        """
        Get a counselor by email.
        
        Args:
            email (str): Counselor email
            
        Returns:
            dict: Counselor data
            
        Raises:
            HTTPException: If counselor is not found
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("email", email).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Counselor with email {email} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving counselor: {str(e)}")

    async def get_counselors(self, limit: int = 100, offset: int = 0):
        """
        Get a list of counselors with pagination.
        
        Args:
            limit (int, optional): Maximum number of counselors to return. Defaults to 100.
            offset (int, optional): Number of counselors to skip. Defaults to 0.
            
        Returns:
            list: List of counselors
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table(self.table).select("*").range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving counselors: {str(e)}")
    
    async def get_counselors_by_school(self, school_id: str):
        """
        Get counselors by school.
        
        Args:
            school_id (str): School name
            
        Returns:
            list: List of counselors
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("school_id", school_id).execute()
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving counselors: {str(e)}")

    async def update_counselor(self, counselor_id: int, counselor: CounselorUpdate):
        """
        Update a counselor by ID.
        
        Args:
            counselor_id (int): Counselor ID
            counselor (CounselorUpdate): Updated counselor data
            
        Returns:
            dict: Updated counselor data
            
        Raises:
            HTTPException: If counselor update fails
        """
        try:
            # Filter out None values
            update_data = {k: v for k, v in counselor.dict().items() if v is not None}
            
            # Update counselor in database
            result = self.supabase.table(self.table).update(update_data).eq("id", counselor_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Counselor with ID {counselor_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating counselor: {str(e)}")

    async def delete_counselor(self, counselor_id: int):
        """
        Delete a counselor by ID.
        
        Args:
            counselor_id (int): Counselor ID
            
        Returns:
            dict: Deleted counselor data
            
        Raises:
            HTTPException: If counselor deletion fails
        """
        try:
            result = self.supabase.table(self.table).delete().eq("id", counselor_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Counselor with ID {counselor_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting counselor: {str(e)}")