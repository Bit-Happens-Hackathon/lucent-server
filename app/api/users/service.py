"""
User service module.
This module contains the business logic for user operations.
"""
import json
import random
import string
from fastapi import HTTPException
from supabase import Client
from datetime import date, datetime
from openai import OpenAI
from app.api.prompts import default_prompts
from app.api.users.model import UserCreate, UserUpdate, ChatCreate, ChatUpdate, MessageCreate, UserLogin
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
        Create a new user with authentication and database entry.
        
        Args:
            user (UserCreate): User data with name, email, password, birthdate, and school
            
        Returns:
            dict: Created user data with ID and other details
            
        Raises:
            HTTPException: If user creation fails in either step
        """
        try:
            # Step 1: Create the authenticated user
            try:
                #ensure passwords match
                if user.password != user.confirm_password:
                    raise HTTPException(
                        status_code=401,
                        detail="Passwords do not match"
                    )
                # Use the password provided by the user
                auth_response = self.supabase.auth.admin.create_user({
                    "email": user.email,
                    "password": user.password,
                    "email_confirm": False
                })
                
                auth_id = auth_response.user.id
                print(f"Created auth user with ID: {auth_id}")
                
            except Exception as auth_error:
                print(f"Auth user creation failed: {str(auth_error)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Authentication account creation failed: {str(auth_error)}"
                )
                
            # Step 2: Create the database user (excluding password fields)
            try:
                # Convert user to a dictionary, excluding password fields
                user_dict = {
                    "name": user.name,
                    "email": user.email,
                    "birthdate": str(user.birthdate),
                    "school": user.school,
                    "auth_id": auth_id
                }
                
                # Insert user into database
                result = self.supabase.table(self.table).insert(user_dict).execute()
                
                if not result.data:
                    # Roll back auth user if DB creation fails
                    try:
                        self.supabase.auth.admin.delete_user(auth_id)
                    except:
                        pass  # Best effort cleanup
                    
                    raise HTTPException(status_code=500, detail="Failed to create database user record")
                    
                # Transform the response to match expected model
                user_data = result.data[0]
                
                return {
                    "id": user_data["email"],
                    "name": user_data["name"],
                    "email": user_data["email"],
                    "birthdate": user_data["birthdate"],
                    "school": user_data["school"],
                    "auth_id": auth_id,
                    "created_at": datetime.now().isoformat()
                }
                
            except Exception as db_error:
                # Try to roll back auth user if something fails
                try:
                    self.supabase.auth.admin.delete_user(auth_id)
                except:
                    pass  # Best effort cleanup
                    
                print(f"Database user creation failed: {str(db_error)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Database user creation failed: {str(db_error)}"
                )
                
        except Exception as e:
            print(f"User creation process failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
        
    # Sign in
    async def sign_in(self, user: UserLogin):
        """
        Sign in a user with email and password.
        
        Args:
            user (UserLogin): User data containing email and password
            
        Returns:
            dict: User data
            
        Raises:
            HTTPException: If sign-in fails
        """
        try:
            # Authenticate the user
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": user.email,
                "password": user.password
            })
            
            if not auth_response.user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
            # Get user data from the database
            # Get user data from the database using the auth_id from the response
            result = self.supabase.table(self.table).select("*").eq("auth_id", auth_response.user.id).execute()
            
            if not result.data:
                raise HTTPException(status_code=404, detail="User database record not found")
                
            user_data = result.data[0]
            # Ensure the 'id' field exists in the response
            if 'id' not in user_data:
                user_data['id'] = user_data['email']  # Use email as id if id is missing
            return user_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error signing in: {str(e)}")

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
            previous_wellness = self.supabase.table("User_Wellness").select("*").eq("user_id", user_id).order("date", desc=True).limit(1).execute()

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
                    inject_prompt = " Here are the Resources available for the user's school: " + str(resources) + " Here is the most recent wellness of the user: " + previous_wellness + " " 
             
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

                # Update the wellness accordingly
                try:
                    wellness_result = await self.update_wellness_from_messages(updated_messages, user_id, previous_wellness)
                    print("Wellness update result:", wellness_result)
                except Exception as e:
                    print(f"Error calling update_wellness_from_messages: {str(e)}")
                    import traceback
                    print(traceback.format_exc())              
                
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

    async def update_wellness_from_messages(self, messages: list, user_id, previous_wellness):
        """
        Analyze chat messages and update user wellness metrics.
        
        Args:
            messages (list): List of chat message objects
            user_id (str): User email ID
            previous_wellness (dict): Previous wellness scores to use as fallback
            
        Returns:
            dict: Result of the wellness update operation
        """
        try:
            # Get the wellness prompt
            wellness_prompt = default_prompts["wellness_prompt"]
            
            # Convert messages to a string representation
            full_prompt = f"{wellness_prompt}\n\nConversation:\n{messages}"
            
            # Ask LLM to analyze and provide wellness scores
            response = self.openai_client.responses.create(
                model="gpt-4.1",
                input=full_prompt
            )
            
            # Parse the LLM's response to extract wellness scores
            response_text = response.output_text.strip()
            wellness_data = self._parse_wellness_response(response_text)
            # If we couldn't parse any data, try again with a clearer prompt
            if not wellness_data:
                for msg in messages[-5:]:  # Use just the last 5 messages to keep it focused
                    if "content" in msg and "sender" in msg:
                        wellness_prompt += f"\n{msg['sender']}: {msg['content']}"
                
                # Make the second attempt
                retry_response = self.openai_client.responses.create(
                    model="gpt-4.1",
                    input=wellness_prompt
                )
                
                # Parse the retry response
                retry_text = retry_response.output_text.strip()
                wellness_data = self._parse_wellness_response(retry_text)
                
                # If still no data, raise an exception
                if not wellness_data:
                    raise ValueError("Could not extract wellness data from the LLM response after retry")
            
            # Define the required categories (all lowercase)
            required_categories = [
                "physical", "financial", "emotional",
                "spiritual", "social", "environmental", "creative"
            ]
            
            # Process and validate scores, filling in with previous values when needed
            validated_data = self._validate_wellness_scores(
                wellness_data, previous_wellness, required_categories
            )
            
            # Prepare data for database - all keys are lowercase as expected by DB
            update_data = {
                "user_id": user_id,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add each category score
            for category in required_categories:
                update_data[category] = validated_data[category]
            
            # Insert into database
            result = self.supabase.table("User_Wellness").insert(update_data).execute()
            
            return {"success": True, "data": result.data if hasattr(result, 'data') else result}
        
        except json.JSONDecodeError as e:
            # Try to salvage what we can by using the previous wellness data
            update_data = self._create_fallback_update(user_id, previous_wellness)
            
            try:
                # Insert into database using fallback data
                result = self.supabase.table("User_Wellness").insert(update_data).execute()
                return {
                    "success": True, 
                    "data": result.data if hasattr(result, 'data') else result,
                    "note": "Used previous wellness due to parsing error"
                }
            except Exception as fallback_error:
                return {
                    "success": False, 
                    "error": f"Failed to parse LLM response and fallback failed: {str(e)}"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Error in update_wellness_from_messages: {str(e)}"}
            
    # Helper methods extracted from the main function
    def _parse_wellness_response(self, response_text):
        """Parse the LLM response to extract wellness data."""
        wellness_data = {}
        
        # Handle array format [{"key": value}, {"key": value}]
        if response_text.startswith('[') and response_text.endswith(']'):
            try:
                wellness_items = json.loads(response_text)
                
                if isinstance(wellness_items, list):
                    for item in wellness_items:
                        if isinstance(item, dict):
                            for category, score in item.items():
                                wellness_data[category.lower()] = score
            except Exception:
                pass
        else:
            # Handle object format {"key": value, "key": value}
            try:
                # Extract JSON from the response using regex
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                
                if json_match:
                    json_str = json_match.group(0)
                    data = json.loads(json_str)
                    for category, score in data.items():
                        wellness_data[category.lower()] = score
                else:
                    # Try direct parsing
                    data = json.loads(response_text)
                    for category, score in data.items():
                        wellness_data[category.lower()] = score
            except Exception:
                pass
                
        return wellness_data
        
    def _validate_wellness_scores(self, wellness_data, previous_wellness, required_categories):
        """Validate wellness scores and fill missing values."""
        validated_data = {}
        
        # First process the returned wellness data
        for category in required_categories:
            value = self._get_category_value(wellness_data, category)
                
            # If we found a value, validate it
            if value is not None:
                try:
                    # Convert to integer if it's not already
                    int_value = int(value) if not isinstance(value, int) else value
                    
                    # Ensure it's in the valid range
                    validated_data[category] = max(0, min(100, int_value))
                except (ValueError, TypeError):
                    # Try to use previous wellness value
                    if category in previous_wellness and previous_wellness[category] is not None:
                        validated_data[category] = previous_wellness[category]
                    else:
                        validated_data[category] = 50
        
        # Fill in missing categories from previous wellness
        for category in required_categories:
            if category not in validated_data:
                prev_value = self._get_previous_value(previous_wellness, category)
                
                if prev_value is not None:
                    validated_data[category] = prev_value
                else:
                    # No previous value available, use default
                    validated_data[category] = 50
                
        return validated_data
        
    def _get_category_value(self, data_dict, category):
        """Get category value with case-insensitive matching."""
        if category in data_dict:
            return data_dict[category]
        elif category.capitalize() in data_dict:
            return data_dict[category.capitalize()]
        return None
        
    def _get_previous_value(self, previous_wellness, category):
        """Get previous value with case-insensitive matching."""
        if category in previous_wellness and previous_wellness[category] is not None:
            return previous_wellness[category]
        elif category.capitalize() in previous_wellness and previous_wellness[category.capitalize()] is not None:
            return previous_wellness[category.capitalize()]
        return None
        
    def _create_fallback_update(self, user_id, previous_wellness):
        """Create fallback update data from previous wellness."""
        required_categories = [
            "physical", "financial", "emotional",
            "spiritual", "social", "environmental", "creative"
        ]
        
        update_data = {
            "user_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Copy values from previous wellness where available
        for category in required_categories:
            if category in previous_wellness and previous_wellness[category] is not None:
                update_data[category] = previous_wellness[category]
            else:
                update_data[category] = 50  # Default
                
        return update_data