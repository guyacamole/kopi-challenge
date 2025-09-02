from django.db import models
import uuid

# Create your models here.


class Conversation(models.Model):
    """
    Represents a debate conversation with a specific topic and bot stance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.TextField(help_text="The debate topic")
    bot_stance = models.TextField(help_text="The position the bot should defend")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.topic} - Bot defends: {self.bot_stance}"

    def get_recent_messages(self, limit=5, reverse=False):
        """Get the most recent messages for this conversation."""
        return self.messages.select_related('role').order_by('created_at' if reverse else '-created_at')[:limit]


class Role(models.Model):
    """
    Represents the role of a message sender (user or bot).
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'

    def __str__(self):
        return self.name.title()


class Message(models.Model):
    """
    Represents a single message in a conversation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    content = models.TextField(help_text="The message content")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return f"{self.conversation.topic} - {self.role.name}: {self.content[:50]}..."
