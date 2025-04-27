"""
User routes module.
This module defines the API endpoints for user operations.
"""
from http.client import HTTPException
from fastapi import APIRouter, Depends, Query
from typing import List
from fastapi import Body

from app.database import get_supabase_client
from app.api.users.service import (
    UserService,
    UserCreate,
    UserUpdate,
    ChatCreate,
    ChatUpdate,
)
from app.api.users.model import UserCreate, UserLogin, UserResponse

# Create router
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# Dependency for UserService
def get_user_service():
    """
    Dependency for UserService.
    
    Returns:
        UserService: User service instance
    """
    return UserService(get_supabase_client())


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Create a new user.
    Args:
        user (UserCreate): User data containing school name, email, and birthdate
        user_service (UserService): User service instance
    Returns:
        UserResponse: Created user data
    """
    return await user_service.create_user(user)

@router.post("/signin", response_model=UserResponse, status_code=201)
async def sign_in_user(
    user: UserLogin = Body(...),
    user_service: UserService = Depends(get_user_service)
):
    """
    Sign in a user.
    
    Args:
        user (UserLogin): User data containing email and password
        user_service (UserService): User service instance
        
    Returns:
        UserResponse: Signed-in user data
    """
    return await user_service.sign_in(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Get a user by ID.
    
    Args:
        user_id (str): User ID
        user_service (UserService): User service instance
        
    Returns:
        UserResponse: User data
    """
    return await user_service.get_user(user_id)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get a list of users with pagination.
    
    Args:
        limit (int, optional): Maximum number of users to return. Defaults to 100.
        offset (int, optional): Number of users to skip. Defaults to 0.
        user_service (UserService): User service instance
        
    Returns:
        List[UserResponse]: List of users
    """
    return await user_service.get_users(limit, offset)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Update a user by ID.
    
    Args:
        user_id (str): User ID
        user (UserUpdate): Updated user data
        user_service (UserService): User service instance
        
    Returns:
        UserResponse: Updated user data
    """
    return await user_service.update_user(user_id, user)


@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete a user by ID.
    
    Args:
        user_id (str): User ID
        user_service (UserService): User service instance
        
    Returns:
        UserResponse: Deleted user data
    """
    return await user_service.delete_user(user_id)

# --------------------------------------------------
# ------------ Chat routes ----------------
# --------------------------------------------------

"""
User routes module extension for chats.
These routes should be added to your existing user router.
"""
from app.api.users.model import ChatCreate, ChatResponse, ChatUpdate, MessageCreate

@router.post("/{user_id}/chats", response_model=ChatResponse, status_code=201)
async def create_user_chat(
    user_id: str,
    chat: ChatCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Create a new chat for a user.
    
    Args:
        user_id (str): User email
        chat (ChatCreate): Chat data
        user_service (UserService): User service instance
        
    Returns:
        ChatResponse: Created chat data
    """
    # Ensure the user_id in the URL matches the one in the request body
    if user_id != chat.user_id:
        raise HTTPException(status_code=400, detail="User ID in URL does not match user_id in request body")
    
    return await user_service.create_user_chat(chat)

@router.get("/{user_id}/chats/{chat_id}", response_model=ChatResponse)
async def get_user_chat(
    user_id: str,
    chat_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Get a chat by ID for a specific user.
    
    Args:
        user_id (str): User email
        chat_id (int): Chat ID
        user_service (UserService): User service instance
        
    Returns:
        ChatResponse: Chat data
    """
    chat = await user_service.get_user_chat(chat_id)
    
    # Ensure the chat belongs to the specified user
    if chat["user_id"] != user_id:
        raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found for user {user_id}")
    
    return chat

@router.get("/{user_id}/chats", response_model=List[ChatResponse])
async def get_user_chats(
    user_id: str,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get all chats for a user with pagination.
    
    Args:
        user_id (str): User email
        limit (int, optional): Maximum number of chats to return. Defaults to 100.
        offset (int, optional): Number of chats to skip. Defaults to 0.
        user_service (UserService): User service instance
        
    Returns:
        List[ChatResponse]: List of chats
    """
    return await user_service.get_user_chats(user_id, limit, offset)

@router.put("/{user_id}/chats/{chat_id}", response_model=ChatResponse)
async def update_user_chat(
    user_id: str,
    chat_id: int,
    chat: ChatUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Update a chat by ID for a specific user.
    
    Args:
        user_id (str): User email
        chat_id (int): Chat ID
        chat (ChatUpdate): Updated chat data
        user_service (UserService): User service instance
        
    Returns:
        ChatResponse: Updated chat data
    """
    # First check if chat belongs to user
    existing_chat = await user_service.get_user_chat(chat_id)
    
    if existing_chat["user_id"] != user_id:
        raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found for user {user_id}")
    
    return await user_service.update_user_chat(chat_id, chat)

@router.delete("/{user_id}/chats/{chat_id}", response_model=ChatResponse)
async def delete_user_chat(
    user_id: str,
    chat_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete a chat by ID for a specific user.
    
    Args:
        user_id (str): User email
        chat_id (int): Chat ID
        user_service (UserService): User service instance
        
    Returns:
        ChatResponse: Deleted chat data
    """
    # First check if chat belongs to user
    existing_chat = await user_service.get_user_chat(chat_id)
    
    if existing_chat["user_id"] != user_id:
        raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found for user {user_id}")
    
    return await user_service.delete_user_chat(chat_id)

@router.post("/{user_id}/chats/{chat_id}/messages", response_model=ChatResponse)
async def add_message_to_chat(
    user_id: str,
    chat_id: int,
    message: MessageCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Add a message to a chat for a specific user.
    
    Args:
        user_id (str): User email
        chat_id (int): Chat ID
        message (MessageCreate): Message data
        user_service (UserService): User service instance
        
    Returns:
        ChatResponse: Updated chat data
    """
    # First check if chat belongs to user
    existing_chat = await user_service.get_user_chat(chat_id)
    
    if existing_chat["user_id"] != user_id:
        raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found for user {user_id}")
    
    return await user_service.add_message_to_chat(chat_id, message)


@router.post("/{user_id}/chat", response_model=dict)
async def chat_with_ai(
    user_id: str,
    data: dict = Body(...),
    user_service: UserService = Depends(get_user_service)
):
    """
    Chat with AI and save the conversation.
    
    Args:
        user_id (str): User email
        data (dict): Request data including prompt and optional chat_id
        user_service (UserService): User service instance
        
    Returns:
        dict: AI response, chat_id, and school resources
    """
    # Get the user to verify existence and get the school
    user = await user_service.get_user(user_id)
    user_school = user["school"]  # Make sure we're getting the school properly
    
    prompt = data.get("prompt")
    chat_id = data.get("chat_id")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    return await user_service.get_openai_response(prompt, user_id, user_school, chat_id)

@router.get("/{user_id}/chats/{chat_id}", response_model=dict)
async def get_chat_history(
    user_id: str,
    chat_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Get chat history.
    
    Args:
        user_id (str): User email
        chat_id (int): Chat ID
        user_service (UserService): User service instance
        
    Returns:
        dict: Chat history
    """
    # Get the chat
    chat = await user_service.get_chat_history(chat_id)
    
    # Verify the chat belongs to the user
    if chat["user_id"] != user_id:
        raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found for user {user_id}")
    
    return chat

@router.get("/{user_id}/recent-chats", response_model=List[dict])
async def get_recent_chats(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    user_service: UserService = Depends(get_user_service)
):
    """
    Get recent chats for a user.
    
    Args:
        user_id (str): User email
        limit (int, optional): Maximum number of chats to return. Defaults to 10.
        user_service (UserService): User service instance
        
    Returns:
        List[dict]: List of recent chats
    """
    return await user_service.get_user_recent_chats(user_id, limit)

@router.post("/{user_id}/chats/{chat_id}/system-message", response_model=dict)
async def add_system_message(
    user_id: str,
    chat_id: int,
    data: dict = Body(...),
    user_service: UserService = Depends(get_user_service)
):
    """
    Add a system message to the chat.
    
    Args:
        user_id (str): User email
        chat_id (int): Chat ID
        data (dict): Request data including system_message
        user_service (UserService): User service instance
        
    Returns:
        dict: Updated chat data
    """
    # Get the chat to verify ownership
    chat = await user_service.get_chat_history(chat_id)
    
    # Verify the chat belongs to the user
    if chat["user_id"] != user_id:
        raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found for user {user_id}")
    
    system_message = data.get("system_message")
    if not system_message:
        raise HTTPException(status_code=400, detail="System message is required")
    
    return await user_service.add_message_to_context(chat_id, system_message)