import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse, Http404
import json
from .schemas import DebateCreate, Debate, DebateGet
from .modules.services.debate_service import create_debate, get_debate, continue_debate
import uuid
from .modules.utils.validate_uuid import validate_uuid

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class DebateAPIViewPost(View):
  def post(self, request):
    """Create or continue a debate."""
    try:
      data: dict = json.loads(request.body)
      debate_create: DebateCreate = DebateCreate(**data)
      if debate_create.conversation_id is None:
        debate: Debate = create_debate(debate_create.user_message)
      else:
        debate: Debate = continue_debate(debate_create)
      json_data = debate.model_dump(exclude_none=True)
      return JsonResponse(json_data)
    except json.JSONDecodeError:
      return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error creating debate: {e}")
      return JsonResponse({'error': str(e)}, status=500)
  
@method_decorator(csrf_exempt, name='dispatch')
class DebateAPIView(View):
  def get(self, request, conversation_id):
    """Get debate by conversation ID."""
    try:
      conversation_id = validate_uuid(conversation_id)
      debate = get_debate(DebateGet(conversation_id=conversation_id, max_messages=20))
    except Http404:
      return JsonResponse({'error': 'Conversation not found'}, status=404)
    except ValueError as e:
      return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
      logger.error(f"Error getting debate: {e}")
      return JsonResponse({'error': 'something went wrong'}, status=500)
    return JsonResponse(debate.model_dump())
