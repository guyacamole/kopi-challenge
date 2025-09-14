from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse, Http404
import json
from .schemas import MessageCreate, MessageUpdate
from .modules.services.messages_service import create_message, get_all_messages, delete_message, update_message, get_message
import pydantic
import logging
from .modules.utils.validate_uuid import validate_uuid
logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class MessagesAPIViewPost(View):
  def post(self, request):
    """Create new message."""
    try:
      data = json.loads(request.body)
      message_create = MessageCreate(**data)
      message = create_message(message_create)
    except json.JSONDecodeError:
      return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except pydantic.ValidationError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error creating message: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse({
        'id': str(message.id),
        'content': message.content
    })

  def get(self, request):
    """Get all messages."""
    try:
      messages = get_all_messages()
    except Exception as e:
      logger.error(f"Error getting messages: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse({
        'messages': list(messages)
    })


@method_decorator(csrf_exempt, name='dispatch')
class MessagesAPIView(View):

  def get(self, request, message_id):
    """Get message by ID."""
    try:
      message_id = validate_uuid(message_id)
      message = get_message(message_id)
    except Http404:
      return JsonResponse({'error': 'Message not found'}, status=404)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error getting messages: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse({
        'id': str(message.id),
        'content': message.content
    })

  def delete(self, request, message_id):
    """Delete message."""
    try:
      message_id = validate_uuid(message_id)
      delete_message(message_id)
    except Http404:
      return JsonResponse({'error': 'Message not found'}, status=404)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error deleting message: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse({'message': 'Message deleted successfully'})

  def put(self, request, message_id):
    """Update message."""
    try:
      message_id = validate_uuid(message_id)
      data = json.loads(request.body)
      message_update = MessageUpdate(**data)
      message = update_message(message_id, message_update)
    except Http404:
      return JsonResponse({'error': 'Message not found'}, status=404)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error deleting message: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse({
        'id': str(message.id),
        'content': message.content
    })
