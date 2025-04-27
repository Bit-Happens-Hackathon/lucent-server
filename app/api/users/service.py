"""
User service module.
This module contains the business logic for user operations.
"""
from fastapi import HTTPException
from supabase import Client
from datetime import date

from app.api.users.model import UserCreate, UserUpdate

class UserService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "users"

    async def create_user(self, user: UserCreate):
        """
        Create a new user in the database.
        
        Args:
            user (UserCreate): User data
            
        Returns:
            dict: Created user data
            
        Raises:
            HTTPException: If user creation fails
        """
        try:
            # Convert date to string for Supabase
            user_dict = user
            user_dict["birthdate"] = str(user.birthdate)
            
            # Insert user into database
            result = self.supabase.table(self.table).insert(user_dict).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create user")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

    async def get_user(self, user_id: str):
        """
        Get a user by ID.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User data
            
        Raises:
            HTTPException: If user is not found
        """
        try:
            result = self.supabase.table(self.table).select("*").eq("id", user_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

    async def get_users(self, limit: int = 100, offset: int = 0):
        """
        Get a list of users with pagination.
        
        Args:
            limit (int, optional): Maximum number of users to return. Defaults to 100.
            offset (int, optional): Number of users to skip. Defaults to 0.
            
        Returns:
            list: List of users
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table(self.table).select("*").range(offset, offset + limit - 1).execute()
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")

    async def update_user(self, user_id: str, user: UserUpdate):
        """
        Update a user by ID.
        
        Args:
            user_id (str): User ID
            user (UserUpdate): Updated user data
            
        Returns:
            dict: Updated user data
            
        Raises:
            HTTPException: If user update fails
        """
        try:
            # Filter out None values
            update_data = {k: v for k, v in user.items() if v is not None}
            
            # Convert date to string if present
            if "birthdate" in update_data and isinstance(update_data["birthdate"], date):
                update_data["birthdate"] = str(update_data["birthdate"])
            
            # Update user in database
            result = self.supabase.table(self.table).update(update_data).eq("id", user_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

    async def delete_user(self, user_id: str):
        """
        Delete a user by ID.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Deleted user data
            
        Raises:
            HTTPException: If user deletion fails
        """
        try:
            result = self.supabase.table(self.table).delete().eq("id", user_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")