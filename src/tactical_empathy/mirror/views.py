from django.shortcuts import render, get_object_or_404
import logging
from .models import Conversation

logger = logging.getLogger(__name__)

# Create your views here.


def index(request):
  """Homepage showing conversation interface."""
  return render(request, 'mirror/index.html')


def create(request):
  """Create new conversation page."""
  return render(request, 'mirror/create.html')


def list_conversations(request):
  """List all conversations page."""
  conversations = Conversation.objects.filter(is_active=True)
  return render(request, 'mirror/list.html', {'conversations': conversations})


def detail(request, id):
  """Conversation detail page."""
  conversation = get_object_or_404(Conversation, id=id)
  messages = conversation.get_recent_messages(limit=14)
  messages = reversed(messages)
  return render(request, 'mirror/detail.html', {
      'conversation': conversation,
      'messages': messages
  })
