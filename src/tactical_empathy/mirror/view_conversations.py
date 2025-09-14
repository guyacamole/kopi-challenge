"""
API views for the conversation functionality.
This module contains API endpoints separated from the main views for better organization.
"""
from .modules.services.conversations_service import create_conversation, update_conversation, delete_conversation, get_all_conversations, get_conversation
from .schemas import ConversationCreate, ConversationUpdate
from .modules.utils.validate_uuid import validate_uuid
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse, Http404
from django.views import View
import pydantic
import logging
import json

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ConversationAPIView(View):
  def post(self, request):
    """Create new conversation."""
    try:
      data = json.loads(request.body)
      conversation_create = ConversationCreate(**data)
      conversation = create_conversation(conversation_create)
    except json.JSONDecodeError:
      return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except pydantic.ValidationError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error creating conversation: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse({
        'id': str(conversation.id),
        'topic': conversation.topic,
        'bot_stance': conversation.bot_stance,
        'created_at': conversation.created_at.isoformat(),
        'is_active': conversation.is_active
    })

  def get(self, request):
    """Get all conversations."""
    try:
      conversations = get_all_conversations()
      conversations_data = []
      for conversation in conversations:
        conversations_data.append({
            'id': str(conversation.id),
            'topic': conversation.topic,
            'bot_stance': conversation.bot_stance,
            'created_at': conversation.created_at.isoformat(),
            'updated_at': conversation.updated_at.isoformat(),
            'is_active': conversation.is_active
        })
    except pydantic.ValidationError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error getting conversations: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse({'conversations': conversations_data})


@method_decorator(csrf_exempt, name='dispatch')
class ConversationAPIViewWithId(View):
  def get(self, request, conversation_id):
    """Get conversation by ID."""
    try:
      conversation_id = validate_uuid(conversation_id)
      conversation = get_conversation(conversation_id) 
    except Http404:
      return JsonResponse({'error': 'Conversation not found'}, status=404)
    except pydantic.ValidationError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except json.JSONDecodeError:
      return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error getting conversation: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse({
        'id': str(conversation.id),
        'topic': conversation.topic,
        'bot_stance': conversation.bot_stance,
        'created_at': conversation.created_at.isoformat(),
        'updated_at': conversation.updated_at.isoformat(),
        'is_active': conversation.is_active
    })

  def delete(self, request, conversation_id):
    """Delete conversation."""
    try:
      conversation_id = validate_uuid(conversation_id)
      delete_conversation(conversation_id)
      return JsonResponse({'message': 'Conversation deleted successfully'})
    except Http404:
      return JsonResponse({'error': 'Conversation not found'}, status=404)
    except pydantic.ValidationError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except json.JSONDecodeError:
      return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error deleting conversation: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)

  def put(self, request, conversation_id):
    """Update conversation."""
    try:
      conversation_id = validate_uuid(conversation_id)
      data = json.loads(request.body)
      data['id'] = conversation_id
      conversation_update = ConversationUpdate(**data)
      conversation = update_conversation(
          conversation_update)
      return JsonResponse({
          'id': str(conversation.id),
          'topic': conversation.topic,
          'bot_stance': conversation.bot_stance,
          'created_at': conversation.created_at.isoformat(),
          'updated_at': conversation.updated_at.isoformat(),
          'is_active': conversation.is_active
      })
    except Http404:
      return JsonResponse({'error': 'Conversation not found'}, status=404)
    except pydantic.ValidationError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except json.JSONDecodeError:
      return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error updating conversation: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
