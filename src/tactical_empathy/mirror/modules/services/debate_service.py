from ...schemas import DebateCreate, Debate, DebateContext, DebateGet, MessageCreate
from ..utils.openAI_provider import get_openai_provider, OpenAIProvider
from ...models import Conversation
from ...models import Message
from ...models import Role
from django.shortcuts import get_object_or_404


def continue_debate(debate_create: DebateCreate) -> Debate:
  """Continue a debate."""
  openai_provider = get_openai_provider()
  conversation: Conversation = get_object_or_404(
      Conversation, id=debate_create.conversation_id)
  messages = Message.objects.filter(conversation=conversation).order_by('created_at')
  # Convert Django Message objects to dictionaries for OpenAI provider
  conversation_history = [
      {
          'role': message.role.name,
          'content': message.content
      }
      for message in messages
  ]
  debate_context: DebateContext = DebateContext(
      topic=conversation.topic,
      bot_stance=conversation.bot_stance,
      conversation_history=conversation_history,
      last_user_message=debate_create.user_message
  )
  response = openai_provider.generate_response(debate_context)
 
  Message.objects.create(
          conversation=Conversation.objects.get(id=conversation.id),
          role=Role.objects.get(name='user'),
          content=debate_create.user_message
      )
  Message.objects.create(
          conversation=Conversation.objects.get(id=conversation.id),
          role=Role.objects.get(name='bot'),
          content=response
      )
  messages: list[Message] = Message.objects.filter(conversation=conversation).order_by('created_at')
  # Convert Django Message instances to MessageCreate instances
  message_creates = [
      MessageCreate(
          content=message.content,
          conversation_id=message.conversation_id,
          role_name=message.role_name
      )
      for message in messages
  ]
  return Debate(
      topic=conversation.topic,
      bot_stance=conversation.bot_stance,
      messages=message_creates,
      user_message=debate_create.user_message,
      conversation_id=debate_create.conversation_id
  )


def create_debate(user_message: str) -> Debate:
  """Create a new debate."""
  openai_provider: OpenAIProvider = get_openai_provider()
  topic, bot_stance = openai_provider.parse_initial_message(user_message)
  conversation: Conversation = Conversation.objects.create(
      topic=topic,
      bot_stance=bot_stance
  )
  debate_create: DebateCreate = DebateCreate(
      conversation_id=conversation.id,
      user_message=user_message
  )
  return continue_debate(debate_create)


def get_debate(debate_get: DebateGet) -> Debate:
  """Get a debate by conversation ID."""
  conversation: Conversation = get_object_or_404(
      Conversation, id=debate_get.conversation_id)
  last_user_message = conversation.messages.filter(
      role=Role.objects.get(name='user')).order_by('created_at').last().content
  if last_user_message is None:
    last_user_message = ''
  messages = list(conversation.messages.select_related(
      'role').order_by('created_at')[:debate_get.max_messages])
  
  # Convert Django Message instances to MessageCreate instances
  message_creates = [
      MessageCreate(
          content=message.content,
          conversation_id=message.conversation_id,
          role_name=message.role_name
      )
      for message in messages
  ]
  
  debate: Debate = Debate(
      topic=conversation.topic,
      bot_stance=conversation.bot_stance,
      messages=message_creates,
      user_message=last_user_message,
      conversation_id=debate_get.conversation_id
  )
  return debate
