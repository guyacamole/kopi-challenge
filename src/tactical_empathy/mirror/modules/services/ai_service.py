"""
AI service for generating persuasive bot responses in debates.
This module handles the core logic for creating convincing arguments using pydantic-ai.
"""

from ...models import Conversation
from ..utils.openAI_provider import get_openai_provider, DebateContext


class DebateBot:
  """
  A debate bot that generates persuasive responses based on conversation context using AI.
  """

  def generate_response(self, conversation: Conversation, user_message: str) -> str:
    """
    The main function to generate a response using the AI provider.
    Args:
      conversation: The conversation to generate a response for.
      user_message: The user's message to generate a response for.
    Returns:
      The generated response.
    """
    # Get OpenAI provider (singleton instance)
    ai_provider = get_openai_provider()

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
  Main function to use the class DebateBot to generate a response.
  This is the function called by views.py
  Args:
    conversation: The conversation to generate a response for.
    user_message: The user's message to generate a response for.
  Returns:
    The generated response.
  """
  return debate_bot.generate_response(conversation, user_message)
