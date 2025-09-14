from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
import json
from .schemas import MessageCreate, MessageUpdate, MessageResponse, MessageListResponse, ErrorResponse, SuccessMessage
from .modules.services.messages_service import create_message, get_all_messages, delete_message, update_message, get_message
import pydantic
import logging
from .modules.utils.validate_uuid import validate_uuid
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


class MessagesAPIViewPost(APIView):
    """API view for creating messages and getting all messages."""

    @extend_schema(
        summary="Create a New Message",
        description="Creates a new message in a conversation.",
        request=MessageCreate,
        responses={
            200: MessageResponse,
            400: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Messages']
    )
    def post(self, request):
        """Create new message."""
        try:
            # Validate request data with Pydantic
            message_create = MessageCreate(**request.data)
            message = create_message(message_create)
            
            response_data = {
                'id': str(message.id),
                'content': message.content,
                'role_name': message.role_name,
                'conversation_id': str(message.conversation_id),
                'created_at': message.created_at.isoformat()
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except pydantic.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get All Messages",
        description="Retrieves a list of all messages.",
        responses={
            200: MessageListResponse,
            500: ErrorResponse
        },
        tags=['Messages']
    )
    def get(self, request):
        """Get all messages."""
        try:
            messages = get_all_messages()
            return Response({'messages': list(messages)}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MessagesAPIView(APIView):
    """API view for managing individual messages by ID."""

    @extend_schema(
        summary="Get Message by ID",
        description="Retrieves a message by its unique identifier.",
        responses={
            200: MessageResponse,
            400: ErrorResponse,
            404: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Messages']
    )
    def get(self, request, message_id):
        """Get message by ID."""
        try:
            message_id = validate_uuid(message_id)
            message = get_message(message_id)
            
            response_data = {
                'id': str(message.id),
                'content': message.content,
                'role_name': message.role_name,
                'conversation_id': str(message.conversation_id),
                'created_at': message.created_at.isoformat()
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error getting message: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Delete Message by ID",
        description="Deletes a message by its unique identifier.",
        responses={
            200: SuccessMessage,
            400: ErrorResponse,
            404: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Messages']
    )
    def delete(self, request, message_id):
        """Delete message."""
        try:
            message_id = validate_uuid(message_id)
            delete_message(message_id)
            return Response({'message': 'Message deleted successfully'}, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Update Message by ID",
        description="Updates a message by its unique identifier.",
        request=MessageUpdate,
        responses={
            200: MessageResponse,
            400: ErrorResponse,
            404: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Messages']
    )
    def put(self, request, message_id):
        """Update message."""
        try:
            message_id = validate_uuid(message_id)
            
            # Validate request data with Pydantic
            message_update = MessageUpdate(**request.data)
            message = update_message(message_id, message_update)
            
            response_data = {
                'id': str(message.id),
                'content': message.content,
                'role_name': message.role_name,
                'conversation_id': str(message.conversation_id),
                'created_at': message.created_at.isoformat()
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        except pydantic.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating message: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
