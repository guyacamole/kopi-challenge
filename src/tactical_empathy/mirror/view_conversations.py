"""
API views for the conversation functionality.
This module contains API endpoints separated from the main views for better organization.
"""
from .modules.services.conversations_service import create_conversation, update_conversation, delete_conversation, get_all_conversations, get_conversation
from .schemas import (
    ConversationCreate, 
    ConversationUpdate, 
    ConversationResponse,
    ConversationListResponse,
    ErrorResponse,
    SuccessMessage
)
from .modules.utils.validate_uuid import validate_uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
import pydantic
import logging
import json
from drf_spectacular.utils import extend_schema
logger = logging.getLogger(__name__)


class ConversationAPIView(APIView):
    """API view for managing conversations."""

    @extend_schema(
        summary="Create a New Conversation",
        description="Creates a new conversation with the specified topic and bot stance.",
        request=ConversationCreate,
        responses={
            200: ConversationResponse,
            400: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Conversation']
    )
    def post(self, request):
        """Create new conversation."""
        try:
            # Validate request data with Pydantic
            conversation_create = ConversationCreate(**request.data)
            conversation = create_conversation(conversation_create)
            
            response_data = {
                'id': str(conversation.id),
                'topic': conversation.topic,
                'bot_stance': conversation.bot_stance,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'is_active': conversation.is_active
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except pydantic.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get All Conversations",
        description="Retrieves a list of all conversations.",
        responses={
            200: ConversationListResponse,
            400: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Conversation']
    )
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
            return Response({'conversations': conversations_data}, status=status.HTTP_200_OK)
            
        except pydantic.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConversationAPIViewWithId(APIView):
    """API view for managing individual conversations by ID."""

    @extend_schema(
        summary="Get a Conversation by ID",
        description="Retrieves a conversation by its unique identifier.",
        responses={
            200: ConversationResponse,
            400: ErrorResponse,
            404: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Conversation']
    )
    def get(self, request, conversation_id):
        """Get conversation by ID."""
        try:
            conversation_id = validate_uuid(conversation_id)
            conversation = get_conversation(conversation_id)
            
            response_data = {
                'id': str(conversation.id),
                'topic': conversation.topic,
                'bot_stance': conversation.bot_stance,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'is_active': conversation.is_active
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        except pydantic.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Delete a Conversation by ID",
        description="Deletes a conversation by its unique identifier.",
        responses={
            200: SuccessMessage,
            400: ErrorResponse,
            404: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Conversation']
    )
    def delete(self, request, conversation_id):
        """Delete conversation."""
        try:
            conversation_id = validate_uuid(conversation_id)
            delete_conversation(conversation_id)
            return Response({'message': 'Conversation deleted successfully'}, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        except pydantic.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Update a Conversation by ID",
        description="Updates a conversation by its unique identifier.",
        request=ConversationUpdate,
        responses={
            200: ConversationResponse,
            400: ErrorResponse,
            404: ErrorResponse,
            500: ErrorResponse
        },
        tags=['Conversation']
    )
    def put(self, request, conversation_id):
        """Update conversation."""
        try:
            conversation_id = validate_uuid(conversation_id)
            
            # Add the conversation_id to the request data for Pydantic validation
            data = dict(request.data)
            data['id'] = conversation_id
            conversation_update = ConversationUpdate(**data)
            conversation = update_conversation(conversation_update)
            
            response_data = {
                'id': str(conversation.id),
                'topic': conversation.topic,
                'bot_stance': conversation.bot_stance,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'is_active': conversation.is_active
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Http404:
            return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)
        except pydantic.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating conversation: {e}")
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
