"""
API views for the chatbot functionality.
This module contains API endpoints separated from the main views for better organization.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from .models import Conversation, Message, Role
from .ai_service import generate_bot_response
from .ai_providers import get_ai_provider

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ChatbotAPIView(View):
  def post(self, request):
    """
    API endpoint for the chatbot challenge.
    Handles conversation creation and message processing.
    Args:
      request: The request object.
    Returns:
      The response object.
    """
    try:
      data = json.loads(request.body)
      conversation_id = data.get('conversation_id')
      user_message = data.get('message', '').strip()
      max_messages = data.get('max_messages', 10)

      if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

      # Get or create roles
      user_role, _ = Role.objects.get_or_create(name='user')
      bot_role, _ = Role.objects.get_or_create(name='bot')

      if conversation_id:
        # Continue existing conversation
        try:
          conversation = Conversation.objects.get(id=conversation_id, is_active=True)
        except Conversation.DoesNotExist:
          return JsonResponse({'error': 'Conversation not found'}, status=404)
      else:
        # Start new conversation - extract topic and bot stance from first message
        # Use AI provider to parse initial message
        ai_provider = get_ai_provider()
        topic, bot_stance = ai_provider.parse_initial_message(user_message)
        conversation = Conversation.objects.create(
            topic=topic,
            bot_stance=bot_stance
        )

      # Save user message
      Message.objects.create(
          conversation=conversation,
          role=user_role,
          content=user_message
      )

      # Generate bot response
      bot_response = generate_bot_response(conversation, user_message)

      # Save bot message
      Message.objects.create(
          conversation=conversation,
          role=bot_role,
          content=bot_response
      )

      # Get recent messages for response
      recent_messages = conversation.get_recent_messages(limit=max_messages)
      message_history = []

      for msg in reversed(recent_messages):
        message_history.append({
            'role': msg.role.name,
            'message': msg.content
        })

      return JsonResponse({
          'conversation_id': str(conversation.id),
          'message': message_history
      })

    except json.JSONDecodeError:
      return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
      return JsonResponse({'error': str(e)}, status=500)


# API endpoint instance
chatbot_api = ChatbotAPIView.as_view()
