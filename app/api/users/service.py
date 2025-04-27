"""
User service module.
This module contains the business logic for user operations.
"""
from fastapi import HTTPException
from supabase import Client
from datetime import date, datetime

from app.api.users.model import UserCreate, UserUpdate, ChatCreate, ChatUpdate, MessageCreate

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
        
# -----------------------------------------------------------------------------------------
# ----------------------------- Chat Service --------------------------------
# -----------------------------------------------------------------------------------------

"""
User service module extension for chats.
These methods should be added to your UserService class.
"""

async def create_user_chat(self, chat: ChatCreate):
    """
    Create a new chat for a user.
    
    Args:
        chat (ChatCreate): Chat data
        
    Returns:
        dict: Created chat data
        
    Raises:
        HTTPException: If chat creation fails
    """
    try:
        # Check if user exists
        user_result = self.supabase.table("User").select("*").eq("Email", chat.user_id).execute()
        
        if not user_result.data:
            raise HTTPException(status_code=404, detail=f"User with email {chat.user_id} not found")
        
        chat_dict = chat.dict()
        
        # Convert messages to JSON string for Supabase
        if "messages" in chat_dict and chat_dict["messages"]:
            chat_dict["messages"] = chat_dict["messages"]
        
        # Insert chat into database
        result = self.supabase.table("User_Chats").insert(chat_dict).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create chat")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating chat: {str(e)}")

async def get_user_chat(self, chat_id: int):
    """
    Get a chat by ID.
    
    Args:
        chat_id (int): Chat ID
        
    Returns:
        dict: Chat data
        
    Raises:
        HTTPException: If chat is not found
    """
    try:
        result = self.supabase.table("User_Chats").select("*").eq("chat_id", chat_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat: {str(e)}")

async def get_user_chats(self, user_id: str, limit: int = 100, offset: int = 0):
    """
    Get all chats for a user with pagination.
    
    Args:
        user_id (str): User email
        limit (int, optional): Maximum number of chats to return. Defaults to 100.
        offset (int, optional): Number of chats to skip. Defaults to 0.
        
    Returns:
        list: List of chats
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Check if user exists
        user_result = self.supabase.table("User").select("*").eq("Email", user_id).execute()
        
        if not user_result.data:
            raise HTTPException(status_code=404, detail=f"User with email {user_id} not found")
        
        result = self.supabase.table("User_Chats").select("*").eq("user_id", user_id).order("date", desc=True).range(offset, offset + limit - 1).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chats: {str(e)}")

async def update_user_chat(self, chat_id: int, chat: ChatUpdate):
    """
    Update a chat by ID.
    
    Args:
        chat_id (int): Chat ID
        chat (ChatUpdate): Updated chat data
        
    Returns:
        dict: Updated chat data
        
    Raises:
        HTTPException: If chat update fails
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in chat.dict().items() if v is not None}
        
        # Update chat in database
        result = self.supabase.table("User_Chats").update(update_data).eq("chat_id", chat_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating chat: {str(e)}")

async def delete_user_chat(self, chat_id: int):
    """
    Delete a chat by ID.
    
    Args:
        chat_id (int): Chat ID
        
    Returns:
        dict: Deleted chat data
        
    Raises:
        HTTPException: If chat deletion fails
    """
    try:
        result = self.supabase.table("User_Chats").delete().eq("chat_id", chat_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chat: {str(e)}")

async def add_message_to_chat(self, chat_id: int, message: MessageCreate):
    """
    Add a message to a chat.
    
    Args:
        chat_id (int): Chat ID
        message (MessageCreate): Message data
        
    Returns:
        dict: Updated chat data
        
    Raises:
        HTTPException: If message addition fails
    """
    try:
        # First get the current chat
        chat_result = self.supabase.table("User_Chats").select("*").eq("chat_id", chat_id).execute()
        
        if not chat_result.data:
            raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found")
        
        current_chat = chat_result.data[0]
        current_messages = current_chat.get("messages", [])
        
        # Create new message with timestamp
        new_message = {
            "content": message.content,
            "sender": message.sender,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add the new message to existing messages
        updated_messages = current_messages + [new_message]
        
        # Update the chat with the new messages
        result = self.supabase.table("User_Chats").update({"messages": updated_messages}).eq("chat_id", chat_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to add message to chat")
            
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding message to chat: {str(e)}")