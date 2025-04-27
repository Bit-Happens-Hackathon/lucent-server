"""
User service module.
This module contains the business logic for user operations.
"""
from fastapi import HTTPException
from supabase import Client
from datetime import date, datetime
from openai import OpenAI
from app.api.prompts import default_prompts
from app.api.users.model import UserCreate, UserUpdate, ChatCreate, ChatUpdate, MessageCreate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Get OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
class UserService:
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.table = "User"
        self.openai_client = OpenAI()

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
        Get a user by ID or email.
        
        Args:
            user_id (str): User ID or email
            
        Returns:
            dict: User data
            
        Raises:
            HTTPException: If user is not found
        """
        try:
            # Check if user_id looks like an email
            result = self.supabase.table(self.table).select("*").eq("email", user_id).execute()

            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"User with identifier {user_id} not found")
                
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
    
    # Get a response from OpenAI
    async def get_openai_response(self, prompt: str, user_id: str, user_school: str, chat_id: int = None):
        """
        Get a response from OpenAI API and save the conversation.
        
        Args:
            prompt (str): Prompt for OpenAI API
            user_id (str): The email of the user
            user_school (str): The school of the user
            chat_id (int, optional): ID of an existing chat to update. If None, a new chat will be created.
            
        Returns:
            dict: Response containing the AI text and chat_id
            
        Raises:
            HTTPException: If OpenAI API call fails or chat operations fail
        """
        try:
            # Load the default prompt
            default_prompt = default_prompts["default_prompt"]
            
            # Get resources for the school (handle many-to-many relationship)
            # First get school's resource relationships
            school_resources_query = self.supabase.table("School_Resource").select("resource_id").eq("school_id", user_school).execute()
            
            inject_prompt = ""
            resources = []
            if school_resources_query.data:
                # Get the actual resources using the IDs from the many-to-many table
                resource_ids = [item["resource_id"] for item in school_resources_query.data]
                
                # Use 'eq' for each resource type
                for resource_id in resource_ids:
                    resource_query = self.supabase.table("Resources").select("*").eq("type", resource_id).execute()
                    if resource_query.data:
                        resources.extend(resource_query.data)
                
                if resources:
                    inject_prompt = " Here are the Resources available for the user's school: " + str(resources) + " "
            
            # Combine prompts
            full_prompt = default_prompt + inject_prompt + prompt
            
            # Call OpenAI API
            response = self.openai_client.responses.create(
                model="gpt-4.1",
                input=full_prompt
            )
            # Get the response text
            ai_response = response.output_text
            
            # Create a timestamp for the current time
            timestamp = datetime.now().isoformat()
            
            # Prepare the new message objects
            user_message = {
                "content": prompt,
                "sender": "user",
                "timestamp": timestamp
            }
            
            ai_message = {
                "content": ai_response,
                "sender": "ai",
                "timestamp": timestamp
            }
            
            # Handle chat storage
            if chat_id is None:
                # Create a new chat
                chat_data = {
                    "user_id": user_id,
                    "messages": [user_message, ai_message],
                    "date": timestamp
                }
                
                # Insert the new chat
                chat_result = self.supabase.table("User_Chats").insert(chat_data).execute()
                
                if not chat_result.data:
                    raise HTTPException(status_code=500, detail="Failed to create chat")
                    
                new_chat_id = chat_result.data[0]["chat_id"]
                
                # Return both the response and the new chat ID
                return {"response": ai_response, "chat_id": new_chat_id, "school_resources": resources if resources else []}
            else:
                # Get the existing chat
                chat_result = self.supabase.table("User_Chats").select("*").eq("chat_id", chat_id).execute()
                
                if not chat_result.data:
                    raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found")
                    
                # Get the current messages
                current_chat = chat_result.data[0]
                current_messages = current_chat.get("messages", [])
                
                # Add the new messages to existing messages
                updated_messages = current_messages + [user_message, ai_message]
                
                # Update the chat with the new messages
                update_result = self.supabase.table("User_Chats").update({"messages": updated_messages}).eq("chat_id", chat_id).execute()
                
                if not update_result.data:
                    raise HTTPException(status_code=500, detail="Failed to update chat")
                    
                # Return both the response and the chat ID
                return {"response": ai_response, "chat_id": chat_id, "school_resources": resources if resources else []}
        
        except Exception as e:
            # Provide more specific error handling
            error_message = str(e)
            if "openai_client" in error_message:
                raise HTTPException(status_code=500, detail=f"OpenAI API error: {error_message}")
            elif "supabase" in error_message:
                raise HTTPException(status_code=500, detail=f"Database error: {error_message}")
            else:
                raise HTTPException(status_code=500, detail=f"Error processing request: {error_message}")
                
    async def get_chat_history(self, chat_id: int):
        """
        Get the chat history by chat ID.
        
        Args:
            chat_id (int): Chat ID
            
        Returns:
            dict: Chat data including messages
            
        Raises:
            HTTPException: If chat is not found
        """
        try:
            result = self.supabase.table("User_Chats").select("*").eq("chat_id", chat_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

    async def get_user_recent_chats(self, user_id: str, limit: int = 10):
        """
        Get recent chats for a user.
        
        Args:
            user_id (str): User email
            limit (int, optional): Maximum number of chats to return. Defaults to 10.
            
        Returns:
            list: List of recent chats
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            result = self.supabase.table("User_Chats").select("*").eq("user_id", user_id).order("date", desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving recent chats: {str(e)}")

    async def add_message_to_context(self, chat_id: int, system_message: str):
        """
        Add a system message to the chat context.
        
        Args:
            chat_id (int): Chat ID
            system_message (str): System message to add
            
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
            
            # Create new system message with timestamp
            new_message = {
                "content": system_message,
                "sender": "system",
                "timestamp": datetime.now().isoformat()
            }
            
            # Add the new message to existing messages
            updated_messages = current_messages + [new_message]
            
            # Update the chat with the new messages
            result = self.supabase.table("User_Chats").update({"messages": updated_messages}).eq("chat_id", chat_id).execute()
            
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to add system message to chat")
                
            return result.data[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding system message: {str(e)}")