from django.db import models
from typing import List
import uuid


class Role(models.Model):
  """
  Represents the role of a message sender (user or bot).
  """
  # Role constants for easy reference
  USER = 'user'
  BOT = 'bot'
  
  ROLE_CHOICES = [
    (USER, 'User'),
    (BOT, 'Bot'),
  ]
  
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    db_table = 'roles'

  def __str__(self):
    return self.name.title()


class Conversation(models.Model):
  """
  Represents a debate conversation with a specific topic and bot stance.
  """
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  topic = models.TextField()
  bot_stance = models.TextField()
  is_active = models.BooleanField(default=True)

  class Meta:
    db_table = 'conversations'

  def __str__(self):
    return f"{self.topic} - Bot defends: {self.bot_stance}"

  def get_recent_messages(self, limit: int = 5, reverse: bool = False) -> List['Message']:
    """Get the most recent messages for this conversation."""
    messages_query = self.messages.all()

    if reverse:
      messages_query = messages_query.order_by('created_at')
    else:
      messages_query = messages_query.order_by('-created_at')

    return list(messages_query[:limit])


class Message(models.Model):
  """
  Represents a single message in a conversation.
  """
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  conversation = models.ForeignKey(
      Conversation, on_delete=models.CASCADE, related_name='messages')
  role = models.ForeignKey(Role, on_delete=models.CASCADE)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    db_table = 'messages'

  def __str__(self):
    return f"{self.conversation.topic} - {self.role.name}: {self.content[:50]}..."

  @property
  def role_name(self):
    """Compatibility property for existing code that expects role_name."""
    return self.role.name

  @property
  def conversation_id(self):
    """Compatibility property for existing code that expects conversation_id."""
    return self.conversation.id
