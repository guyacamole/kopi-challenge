"""
AI service for generating persuasive bot responses in debates.
This module handles the core logic for creating convincing arguments using pydantic-ai.
"""
import logging
from .models import Conversation
from .ai_providers import get_ai_provider, DebateContext

logger = logging.getLogger(__name__)


class DebateBot:
  """
  A debate bot that generates persuasive responses based on conversation context using AI.
  """

  def generate_response(self, conversation: Conversation, user_message: str) -> str:
    """
    Generate a persuasive response based on the conversation context using pydantic-ai.
    """
    # Get AI provider (singleton instance)
    ai_provider = get_ai_provider()

    # Get conversation history
    messages = list(conversation.messages.select_related(
        'role').order_by('created_at'))

    # Build context for AI using pydantic model
    context = DebateContext(
        topic=conversation.topic,
        bot_stance=conversation.bot_stance,
        message_count=len(messages),
        user_message=user_message,
        conversation_history=[
            {
                'role': msg.role.name,
                'content': msg.content
            } for msg in messages[-7:]  # Last 7 messages for context
        ]
    )

    # Generate response using AI provider
    return ai_provider.generate_response(context)


# Global instance
debate_bot = DebateBot()


def generate_bot_response(conversation: Conversation, user_message: str) -> str:
  """
  Main function to generate bot responses.
  This is the function called by views.py
  """
  return debate_bot.generate_response(conversation, user_message)
