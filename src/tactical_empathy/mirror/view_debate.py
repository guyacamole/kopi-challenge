import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
import json
from .schemas import DebateCreate, Debate, DebateGet, DebateResponse, ErrorResponse, SuccessMessage
from .modules.services.debate_service import create_debate, get_debate, continue_debate
import uuid
import pydantic
from .modules.utils.validate_uuid import validate_uuid
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


class DebateAPIViewPost(APIView):
    """API view for creating and continuing debates."""

    @extend_schema(
        summary="Create or Continue a Debate",
        description="Creates a new debate or continues an existing one. If no conversation_id is provided, a new debate is created.",
        request=DebateCreate,
        responses={
            200: DebateResponse,
            400: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Debate']
    )
    def post(self, request):
        """Create or continue a debate."""
        try:
            # Validate request data with Pydantic
            debate_create = DebateCreate(**request.data)
            if debate_create.conversation_id is None:
                debate = create_debate(debate_create.user_message)
            else:
                debate = continue_debate(debate_create)
            
            # Convert Pydantic model to dict for response
            response_data = debate.model_dump(exclude_none=True)
            return Response(response_data, status=status.HTTP_200_OK)
            
        except pydantic.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating debate: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
class DebateAPIView(APIView):
    """API view for retrieving debates by conversation ID."""

    @extend_schema(
        summary="Get Debate by Conversation ID",
        description="Retrieves a debate and its messages by conversation ID.",
        responses={
            200: DebateResponse,
            400: ErrorResponse,
            404: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Debate']
    )
    def get(self, request, conversation_id):
        """Get debate by conversation ID."""
        try:
            conversation_id = validate_uuid(conversation_id)
            debate = get_debate(DebateGet(conversation_id=conversation_id, max_messages=20))
            
            # Convert Pydantic model to dict for response
            response_data = debate.model_dump()
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error getting debate: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
