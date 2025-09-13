from pydantic import BaseModel
from typing import Dict
import uuid
from typing import Optional


class MessageBase(BaseModel):
  """Schema for a message."""
  content: str


class MessageCreate(MessageBase):
  """Schema for creating a message."""
  conversation_id: uuid.UUID
  role_name: str


class MessageUpdate(BaseModel):
  """Schema for updating a message."""
  content: Optional[str] = None
  role_name: Optional[str] = None
  conversation_id: Optional[uuid.UUID] = None


class ConversationCreate(BaseModel):
  """Schema for creating a conversation."""
  topic: str
  bot_stance: str


class ConversationUpdate(BaseModel):
  """Schema for updating a conversation."""
  id: uuid.UUID
  topic: Optional[str]
  bot_stance: Optional[str]


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
  messages: list[MessageCreate]
  conversation_id: uuid.UUID


class DebateGet(BaseModel):
  """Schema for a debate get."""
  max_messages: int
  conversation_id: Optional[uuid.UUID]