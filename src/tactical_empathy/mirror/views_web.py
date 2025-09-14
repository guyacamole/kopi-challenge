from django.shortcuts import render
from .modules.services.conversations_service import get_all_conversations, get_conversation
from .modules.services.messages_service import get_messages_for_conversation
from .modules.utils.validate_uuid import validate_uuid
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


def index(request):
    """Homepage showing conversation interface."""
    return render(request, 'mirror/index.html')


def create(request):
    """Create new conversation page."""
    return render(request, 'mirror/create.html')


def list_conversations(request):
    """List all conversations page."""
    try:
        conversations = get_all_conversations()
        # Filter only active conversations and add message count
        active_conversations = []
        for conv in conversations:
            if conv.is_active:
                # Add message count to each conversation
                try:
                    messages = get_messages_for_conversation(conv.id)
                    conv.message_count = len(messages)
                except Exception:
                    conv.message_count = 0
                active_conversations.append(conv)
        return render(request, 'mirror/list.html', {'conversations': active_conversations})
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        return render(request, 'mirror/list.html', {'conversations': []})


def detail(request, id):
    """Conversation detail page."""
    try:
        conversation_id = validate_uuid(id)
        conversation = get_conversation(conversation_id)
        messages = get_messages_for_conversation(conversation_id, limit=50)
        # Reverse messages to show oldest first (chronological order)
        messages = list(messages)
        return render(request, 'mirror/detail.html', {
            'conversation': conversation,
            'messages': messages
        })
    except ValueError as e:
        logger.error(f"Invalid UUID: {e}")
        raise Http404("Conversation not found")
    except Exception as e:
        logger.error(f"Error getting conversation detail: {e}")
        raise Http404("Conversation not found")
