
from ...schemas import ConversationCreate, ConversationUpdate
from ...models import Conversation
from typing import List
import uuid
from django.http import HttpRequest
from django.shortcuts import get_object_or_404


def create_conversation(conversation_create: ConversationCreate) -> Conversation:
  """Create a new conversation."""
  return Conversation.objects.create(
      topic=conversation_create.topic,
      bot_stance=conversation_create.bot_stance
  )


def get_conversation(conversation_id: uuid.UUID) -> Conversation:
  """Get a conversation by ID."""
  return get_object_or_404(Conversation, id=conversation_id)


def update_conversation(conversation_update: ConversationUpdate, conversation_id: uuid.UUID) -> Conversation:
  """Update a conversation."""
  conversation = get_object_or_404(Conversation, id=conversation_id)
  if conversation_update.topic:
    conversation.topic = conversation_update.topic
  if conversation_update.bot_stance:
    conversation.bot_stance = conversation_update.bot_stance
  conversation.save()
  return conversation


def delete_conversation(conversation_id: uuid.UUID) -> None:
  """Delete a conversation."""
  conversation = get_object_or_404(Conversation, id=conversation_id)
  conversation.delete()


def get_all_conversations() -> List[Conversation]:
  """Get all conversations."""
  return list(Conversation.objects.all())
