from ...models import Message, Conversation, Role
from typing import List
import uuid
from django.shortcuts import get_object_or_404
from ...schemas import MessageCreate, MessageUpdate
from django.http import Http404

def create_message(message_create: MessageCreate) -> Message:
  """Create a new message in a conversation."""
  conversation = get_object_or_404(Conversation, id=message_create.conversation_id)
  try:
    role = get_object_or_404(Role, name=message_create.role_name)
  except Http404:
    raise ValueError('Role not found')
  return Message.objects.create(
      conversation=conversation,
      role=role,
      content=message_create.content
  )


def update_message(message_id: uuid.UUID, message_update: MessageUpdate) -> Message:
  """Update a message."""
  message = get_object_or_404(Message, id=message_id)
  if message_update.content:
    message.content = message_update.content
  if message_update.role_name:
    message.role_name = message_update.role_name
  if message_update.conversation_id:
    message.conversation_id = message_update.conversation_id
  message.save()
  return message


def get_message(message_id: uuid.UUID) -> Message:
  """Get a message by ID."""
  return get_object_or_404(Message, id=message_id)


def get_messages_for_conversation(conversation_id: uuid.UUID, limit: int = None) -> List[Message]:
  """Get all messages for a conversation."""
  conversation = get_object_or_404(Conversation, id=conversation_id)
  messages_query = conversation.messages.select_related('role').order_by('created_at')

  if limit:
    messages_query = messages_query[:limit]

  return list(messages_query)


def delete_message(message_id: uuid.UUID) -> None:
  """Delete a message."""
  message = get_object_or_404(Message, id=message_id)
  message.delete()


def get_recent_messages_for_conversation(conversation_id: uuid.UUID, limit: int = 5) -> List[Message]:
  """Get the most recent messages for a conversation."""
  conversation = get_object_or_404(Conversation, id=conversation_id)
  return conversation.get_recent_messages(limit=limit)


def get_all_messages() -> List[Message]:
  """Get all messages."""
  messages = Message.objects.all()
  messages_data = []
  for message in messages:
    messages_data.append({
        'id': str(message.id),
        'content': message.content,
        'conversation_id': str(message.conversation_id),
        'role_name': message.role_name
    })
  return messages_data
