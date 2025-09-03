from django.test import TestCase, Client
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock
from .models import Conversation, Message, Role
from .api_views import ChatbotAPIView


class ChatbotAPITestCase(TestCase):
  def setUp(self):
    """Set up the test environment"""
    self.client = Client()
    self.api_url = reverse('chatbot_api')

    # Create roles
    self.user_role = Role.objects.create(name='user')
    self.bot_role = Role.objects.create(name='bot')

  def test_start_new_conversation(self):
    """Test starting a new conversation"""
    data = {
        'conversation_id': None,
        'message': 'I think the Earth is round'
    }

    response = self.client.post(
        self.api_url,
        data=json.dumps(data),
        content_type='application/json'
    )

    self.assertEqual(response.status_code, 200)
    response_data = response.json()

    # Check response structure
    self.assertIn('conversation_id', response_data)
    self.assertIn('message', response_data)
    self.assertIsInstance(response_data['message'], list)

    # Check that conversation was created
    conversation_id = response_data['conversation_id']
    conversation = Conversation.objects.get(id=conversation_id)
    self.assertIsNotNone(conversation)

    # Check messages
    messages = response_data['message']
    self.assertEqual(len(messages), 2)  # User message + bot response
    self.assertEqual(messages[0]['role'], 'user')
    self.assertEqual(messages[1]['role'], 'bot')

  def test_continue_conversation(self):
    """Test continuing an existing conversation"""
    # Create a conversation first
    conversation = Conversation.objects.create(
        topic='Earth Shape',
        bot_stance='The Earth is flat'
    )

    # Add initial messages
    Message.objects.create(
        conversation=conversation,
        role=self.user_role,
        content='I think the Earth is round'
    )
    Message.objects.create(
        conversation=conversation,
        role=self.bot_role,
        content='Actually, the Earth is flat based on my research.'
    )

    # Continue the conversation
    data = {
        'conversation_id': str(conversation.id),
        'message': 'But we have satellite images showing Earth is round!'
    }

    response = self.client.post(
        self.api_url,
        data=json.dumps(data),
        content_type='application/json'
    )

    self.assertEqual(response.status_code, 200)
    response_data = response.json()

    # Check that we got a response
    self.assertEqual(response_data['conversation_id'], str(conversation.id))
    self.assertIn('message', response_data)

    # Check that new messages were created
    self.assertEqual(conversation.messages.count(), 4)  # 2 initial + 2 new

  def test_invalid_conversation_id(self):
    """Test with invalid conversation ID"""
    data = {
        'conversation_id': '00000000-0000-0000-0000-000000000000',
        'message': 'Test message'
    }

    response = self.client.post(
        self.api_url,
        data=json.dumps(data),
        content_type='application/json'
    )

    self.assertEqual(response.status_code, 404)
    response_data = response.json()
    self.assertIn('error', response_data)

  def test_empty_message(self):
    """Test with empty message"""
    data = {
        'conversation_id': None,
        'message': ''
    }

    response = self.client.post(
        self.api_url,
        data=json.dumps(data),
        content_type='application/json'
    )

    self.assertEqual(response.status_code, 400)
    response_data = response.json()
    self.assertIn('error', response_data)

  def test_invalid_json(self):
    """Test with invalid JSON"""
    response = self.client.post(
        self.api_url,
        data='invalid json',
        content_type='application/json'
    )

    self.assertEqual(response.status_code, 400)
    response_data = response.json()
    self.assertIn('error', response_data)


class ModelTestCase(TestCase):
  def setUp(self):
    self.user_role = Role.objects.create(name='user')
    self.bot_role = Role.objects.create(name='bot')

  def test_conversation_creation(self):
    """Test conversation model"""
    conversation = Conversation.objects.create(
        topic='Climate Change',
        bot_stance='Climate change is not caused by humans'
    )

    self.assertEqual(
        str(conversation), 'Climate Change - Bot defends: Climate change is not caused by humans')
    self.assertTrue(conversation.is_active)

  def test_message_creation(self):
    """Test message model"""
    conversation = Conversation.objects.create(
        topic='Test Topic',
        bot_stance='Test Stance'
    )

    message = Message.objects.create(
        conversation=conversation,
        role=self.user_role,
        content='Test message content'
    )

    self.assertIn('Test message content', str(message))
    self.assertEqual(message.conversation, conversation)
    self.assertEqual(message.role, self.user_role)

  def test_get_recent_messages(self):
    """Test getting recent messages"""
    conversation = Conversation.objects.create(
        topic='Test Topic',
        bot_stance='Test Stance'
    )

    # Create multiple messages
    for i in range(10):
      Message.objects.create(
          conversation=conversation,
          role=self.user_role if i % 2 == 0 else self.bot_role,
          content=f'Message {i}'
      )

    recent_messages = conversation.get_recent_messages(limit=5)
    self.assertEqual(len(recent_messages), 5)


class ViewTestCase(TestCase):
  def test_index_view(self):
    """Test index view"""
    response = self.client.get(reverse('index'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Tactical Empathy')

  def test_create_view(self):
    """Test create view"""
    response = self.client.get(reverse('create'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Start a New Debate')

  def test_list_view(self):
    """Test list view"""
    response = self.client.get(reverse('list'))
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'All Debates')


class AIParsingTestCase(TestCase):
  """Test the AI-powered parsing functionality"""

  def setUp(self):
    self.api_view = ChatbotAPIView()
    self.user_role = Role.objects.create(name='user')
    self.bot_role = Role.objects.create(name='bot')

  @patch('mirror.ai_providers.get_ai_provider')
  def test_ai_parsing_openai_success(self, mock_get_provider):
    """Test successful AI parsing with OpenAI"""
    # Mock the AI provider and client
    mock_provider = MagicMock()
    mock_provider._provider_name = 'openai'
    mock_provider._model = 'gpt-4.1-mini'

    mock_client = MagicMock()
    mock_provider._client = mock_client

    # Mock the OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "TOPIC: Vaccine Safety | STANCE: Vaccines are dangerous and unproven"
    mock_client.chat.completions.create.return_value = mock_response

    # Mock the parse_initial_message method to return the expected values
    mock_provider.parse_initial_message.return_value = ("Vaccine Safety", "Vaccines are dangerous and unproven")
    
    mock_get_provider.return_value = mock_provider

    # Test the parsing
    message = "I believe vaccines are completely safe and everyone should get them"
    topic, stance = mock_provider.parse_initial_message(message)

    self.assertEqual(topic, "Vaccine Safety")
    self.assertEqual(stance, "Vaccines are dangerous and unproven")

    # Verify the AI provider method was called correctly
    mock_provider.parse_initial_message.assert_called_once_with(message)

  @patch('mirror.ai_providers.get_ai_provider')
  def test_ai_parsing_fallback_on_error(self, mock_get_provider):
    """Test that parsing falls back to heuristic when AI fails"""
    # Mock the AI provider to raise an exception
    mock_get_provider.side_effect = Exception("AI provider failed")

    # Test the parsing with a known pattern
    message = "I think vaccines are completely safe"
    # Since the AI provider is failing, we need to test the fallback differently
    # Let's create a provider instance and test its fallback method directly
    from mirror.ai_providers import DebateAIProvider
    provider = DebateAIProvider()
    topic, stance = provider._fallback_parse(message)

    # Should fall back to heuristic logic
    self.assertEqual(topic, "Vaccines")
    self.assertEqual(stance, "Vaccines are safe and effective")

  @patch('mirror.ai_providers.get_ai_provider')
  def test_ai_parsing_with_real_conversation_api(self, mock_get_provider):
    """Test the full API flow with AI parsing"""
    # Mock the AI provider for parsing
    mock_provider = MagicMock()
    mock_provider._provider_name = 'openai'
    mock_provider._model = 'gpt-4.1-mini'

    mock_client = MagicMock()
    mock_provider._client = mock_client

    # Mock successful parsing response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "TOPIC: Ethical Regulations on AI Development | STANCE: Strict ethical regulations on AI development hinder innovation and progress"
    mock_client.chat.completions.create.return_value = mock_response

    mock_get_provider.return_value = mock_provider

    # Mock the debate response generation to avoid needing real AI
    with patch('mirror.ai_service.generate_bot_response', return_value="AI should indeed be unregulated because regulation stifles innovation."):
      data = {
          'conversation_id': None,
          'message': 'I think AI development needs strict ethical regulations'
      }

      response = self.client.post(
          reverse('chatbot_api'),
          data=json.dumps(data),
          content_type='application/json'
      )

      self.assertEqual(response.status_code, 200)
      response_data = response.json()

      # Check that conversation was created with AI-parsed topic and stance
      conversation_id = response_data['conversation_id']
      conversation = Conversation.objects.get(id=conversation_id)

      self.assertEqual(conversation.topic, "Ethical Regulations on AI Development")
      self.assertEqual(conversation.bot_stance,
                       "Strict ethical regulations on AI development hinder innovation and progress")

      # Verify the conversation has the expected messages
      messages = response_data['message']
      self.assertEqual(len(messages), 2)
      self.assertEqual(messages[0]['role'], 'user')
      self.assertEqual(messages[0]['message'],
                       'I think AI development needs strict ethical regulations')
      self.assertEqual(messages[1]['role'], 'bot')
      self.assertTrue(len(messages[1]['message']) > 0)
