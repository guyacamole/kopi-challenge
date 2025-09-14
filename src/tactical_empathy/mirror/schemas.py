from pydantic import BaseModel, Field
from typing import Dict, List
import uuid
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    """Schema for a message."""
    content: str = Field(..., description="The content of the message", example="Hello, how are you?")


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    conversation_id: uuid.UUID = Field(..., description="The conversation this message belongs to")
    role_name: str = Field(..., description="The role of the message sender", example="user")


class MessageResponse(BaseModel):
    """Schema for a message response."""
    id: uuid.UUID = Field(..., description="Unique identifier for the message")
    content: str = Field(..., description="The content of the message", example="Hello, how are you?")
    role_name: str = Field(..., description="The role of the message sender", example="user")
    conversation_id: uuid.UUID = Field(..., description="The conversation this message belongs to")
    created_at: datetime = Field(..., description="When the message was created")

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    """Schema for list of messages response."""
    messages: List[MessageResponse] = Field(..., description="List of messages")


class MessageUpdate(BaseModel):
    """Schema for updating a message."""
    content: Optional[str] = Field(None, description="The content of the message")
    role_name: Optional[str] = Field(None, description="The role of the message sender")
    conversation_id: Optional[uuid.UUID] = Field(None, description="The conversation this message belongs to")


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    topic: str = Field(..., description="The topic of the conversation", max_length=255, example="Climate Change")
    bot_stance: str = Field(..., description="The bot's stance on the topic", max_length=255, example="Pro-environmental action")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    topic: Optional[str] = Field(None, description="The topic of the conversation", max_length=255)
    bot_stance: Optional[str] = Field(None, description="The bot's stance on the topic", max_length=255)


class DebateContext(ConversationCreate):
  """Context model for debate conversations."""
  last_user_message: str
  conversation_history: list[Dict[str, str]] = []


class DebateCreate(BaseModel):
  """Schema for creating a chat."""
  user_message: str
  conversation_id: Optional[uuid.UUID] = None


class Debate(DebateCreate):
    """Schema for a chat."""
    messages: List[MessageResponse] = Field(..., description="List of messages in the debate")
    conversation_id: uuid.UUID = Field(..., description="The conversation this debate belongs to")


class DebateResponse(BaseModel):
    """Schema for a debate response."""
    conversation_id: uuid.UUID = Field(..., description="The conversation this debate belongs to")
    messages: List[MessageResponse] = Field(..., description="List of messages in the debate")
    user_message: str = Field(..., description="The user's message", example="I think climate change is serious")

    class Config:
        from_attributes = True


class DebateGet(BaseModel):
    """Schema for a debate get."""
    max_messages: int = Field(..., description="Maximum number of messages to retrieve", example=20)
    conversation_id: Optional[uuid.UUID] = Field(None, description="The conversation ID to get debate for")
  
class ConversationResponse(BaseModel):
    """Schema for a single conversation response."""
    id: uuid.UUID = Field(..., description="Unique identifier for the conversation")
    topic: str = Field(..., description="The topic of the conversation", example="Climate Change")
    bot_stance: str = Field(..., description="The bot's stance on the topic", example="Pro-environmental action")
    created_at: datetime = Field(..., description="When the conversation was created")
    updated_at: datetime = Field(..., description="When the conversation was last updated")
    is_active: bool = Field(..., description="Whether the conversation is active", example=True)

    class Config:
        from_attributes = True # Helps Pydantic work with Django models


class ConversationListResponse(BaseModel):
    """Schema for list of conversations response."""
    conversations: List[ConversationResponse] = Field(..., description="List of conversations")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error message describing what went wrong", example="Invalid input data")


class SuccessMessage(BaseModel):
    """Schema for success message responses."""
    message: str = Field(..., description="Success message", example="Operation completed successfully")