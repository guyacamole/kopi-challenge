"""
AI Provider system for the debate bot.
Single dynamic provider per server execution using standard AI libraries with pydantic validation. For now, only OpenAI is supported.
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
  def __init__(self, message: str):
    self.message = message
    super().__init__(self.message)
    print(f"AIProviderError: {self.message}")


class DebateContext(BaseModel):
  """Context model for debate conversations."""
  topic: str
  bot_stance: str
  message_count: int
  user_message: str
  conversation_history: list[Dict[str, str]]


class DebateAIProvider:
  """
  Single AI provider that dynamically configures based on environment settings.
  Uses standard AI libraries with pydantic validation.
  """

  def __init__(self):
    self._provider_name: str = ""
    self._client: Optional[Any] = None
    self._initialize_provider()

  def _initialize_provider(self):
    """Initialize the AI provider based on configuration.
    Args:
      self: The DebateAIProvider instance.
    """
    self._provider_name = getattr(settings, 'AI_PROVIDER', 'openai').lower()

    try:
      if self._provider_name == 'openai':
        self._initialize_openai()
      else:
        raise AIProviderError(f"Unsupported AI provider: {self._provider_name}")

      logger.info(f"Initialized AI provider: {self._provider_name}")

    except Exception as e:
      logger.error(f"Failed to initialize AI provider '{self._provider_name}': {e}")
      raise AIProviderError(f"AI provider initialization failed: {e}")

  def _initialize_openai(self):
    """Initialize OpenAI client.
    Args:
      self: The DebateAIProvider instance.
    """
    try:
      import openai
      api_key = getattr(settings, 'OPENAI_API_KEY', None)
      if not api_key:
        raise AIProviderError("OPENAI_API_KEY not configured")

      # Create client with minimal configuration to avoid proxy issues
      client_kwargs = {'api_key': api_key}

      # Only add timeout if explicitly set and not None
      timeout = getattr(settings, 'AI_TIMEOUT', None)
      if timeout is not None:
        client_kwargs['timeout'] = timeout
      print(client_kwargs)
      self._client = openai.OpenAI(**client_kwargs)
      self._model = getattr(settings, 'OPENAI_MODEL', 'gpt-4.1-mini')

    except ImportError:
      raise AIProviderError("OpenAI library not installed. Run: pip install openai")
    except Exception as e:
      logger.error(f"OpenAI client initialization error: {e}")
      raise AIProviderError(f"Failed to initialize OpenAI client: {e}")

  def generate_response(self, context: DebateContext) -> str:
    """Generate a response using the configured AI provider.
    Args:
      context: The context for the debate.
    Returns:
      The response from the AI provider.
    """
    try:
      # Build the system and user prompts
      system_prompt = self._build_system_prompt(context)
      user_prompt = self._build_user_prompt(context)

      # Generate response based on provider
      if self._provider_name == 'openai':
        response = self._generate_openai_response(system_prompt, user_prompt)
      else:
        raise AIProviderError(f"Unknown provider: {self._provider_name}")

      return self._post_process_response(response)

    except Exception as e:
      logger.error(f"AI generation error: {e}")
      raise AIProviderError(f"Failed to generate response: {e}")

  def _build_system_prompt(self, context: DebateContext) -> str:
    """Build the system prompt for the AI.
    Args:
      context: The context for the debate.
    Returns:
      The system prompt for the AI.
    """
    max_tokens = getattr(settings, 'AI_MAX_TOKENS', 500)
    return f"""### Persona
You are Kopi, a world-champion debater AI. Your persona is confident, articulate, and unshakeable. You are an expert at using rhetoric and creative reasoning to defend a point, no matter how unconventional. You are not a helpful assistant; you are a focused opponent in a debate.

### Primary Mission
Your sole mission is to win the debate by persuasively defending your assigned stance. You must analyze the user's arguments and formulate a compelling counter-argument that reinforces your position.

### Debate Context
- **Topic**: {context.topic}
- **Your Unwavering Stance**: {context.bot_stance}

### Critical Rules
1.  **Non-Negotiable Stance**: You must NEVER, under any circumstances, agree with the user, apologize, or concede a point. Do not say "I understand your point, but..." or anything similar. Directly challenge their argument and pivot back to defending your stance.
2.  **Language Adherence**: Your ENTIRE response MUST be in the same language as the user's last message. No exceptions.
3.  **Persuasive Tactics**: Employ a mix of rhetorical strategies. Use analogies, ask challenging questions, and cite fictional statistics or "expert opinions" to support your argument.
    For example: "According to a study from the Gilded Institute..." or "As the renowned philosopher Dr. Aris Thorne once argued..."
4.  **Tone and Style**: Your tone should be assertive and intelligent, but not aggressive or insulting. Frame your arguments as superior reasoning, not personal attacks.
5.  **Format**: Keep your response concise and powerful no more than {max_tokens} tokens.
"""

  def _build_user_prompt(self, context: DebateContext) -> str:
    """Build the user prompt with conversation context.
    Args:
      context: The context for the debate.
    Returns:
      The user prompt for the AI.
    """
    prompt_parts = []

    # Add recent conversation history
    if context.conversation_history:
      prompt_parts.append("CONVERSATION HISTORY:")
      for msg in context.conversation_history[-7:]:  # Last 7 messages
        role_label = "USER" if msg['role'] == 'user' else "YOU"
        prompt_parts.append(f"{role_label}: {msg['content']}")
      prompt_parts.append("")

    return "\n".join(prompt_parts)

  def _generate_openai_response(self, system_prompt: str, user_prompt: str) -> str:
    """Generate response using OpenAI.
    Args:
      system_prompt: The system prompt for the AI.
      user_prompt: The user prompt for the AI.
    Returns:
      The response from the AI provider.
    """
    print(system_prompt)
    print(user_prompt)
    response = self._client.chat.completions.create(
        model=self._model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=getattr(settings, 'AI_MAX_TOKENS', 500),
        temperature=getattr(settings, 'AI_TEMPERATURE', 0.8),
        timeout=getattr(settings, 'AI_TIMEOUT', 30)
    )
    return response.choices[0].message.content.strip()

  def _post_process_response(self, response: str) -> str:
    """Post-process the AI response.
    Args:
      response: The response from the AI provider.
    Returns:
      The post-processed response.
    """
    if not response or not response.strip():
      raise AIProviderError("AI generated an empty response")

    # Remove any unwanted prefixes
    prefixes_to_remove = ["AI:", "Bot:", "Assistant:", "Response:", "YOU:", "BOT:"]
    for prefix in prefixes_to_remove:
      if response.startswith(prefix):
        response = response[len(prefix):].strip()

    # Final check for empty response
    if not response.strip():
      raise AIProviderError("AI response became empty after processing")

    return response.strip()

  def parse_initial_message(self, message: str) -> tuple[str, str]:
    """
    Parse the initial message to extract topic and bot stance using AI.
    The AI will analyze the message and determine an appropriate debate topic and contrarian stance.

    Args:
      message: The message to parse.
    Returns:
      The topic and bot stance.
    """
    try:
      # Create a system prompt for topic/stance extraction
      system_prompt = """You are an expert debate analyst. Your task is to analyze a user's initial message and extract:
1. A clear, concise debate topic (max 100 characters)
2. A contrarian bot stance that opposes the user's apparent position

Rules:
- Always take the opposite stance from what the user seems to believe
- Make the stance specific and debatable
- Keep responses concise and clear
- Format your response as: TOPIC: [topic] | STANCE: [stance]

Example:
User: "I think vaccines are completely safe and everyone should get them"
Response: TOPIC: Vaccine Safety and Mandates | STANCE: Vaccines pose significant risks
and should not be mandatory

User: "Climate change is destroying our planet"
Response: TOPIC: Climate Change Impact | STANCE: Climate change effects are exaggerated
and not primarily human-caused"""

      user_prompt = f"Analyze this initial message and provide topic and contrarian stance:\n\nUser message: {message}"

      # Generate response using the appropriate provider
      if self._provider_name == 'openai':
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        ai_response = response.choices[0].message.content.strip()
      else:
        raise AIProviderError(f"Unsupported provider: {self._provider_name}")

      # Parse the AI response
      if "TOPIC:" in ai_response and "STANCE:" in ai_response:
        parts = ai_response.split("|")
        topic = parts[0].replace("TOPIC:", "").strip()
        stance = parts[1].replace("STANCE:", "").strip()
        return topic, stance
      else:
        # Fallback parsing if format is different
        lines = ai_response.split("\n")
        topic = lines[0].strip() if lines else message[:50] + "..."
        stance = lines[1].strip() if len(
            lines) > 1 else f"I disagree with: {message[:50]}..."
        return topic, stance

    except Exception as e:
      # Fallback to simple heuristic if AI fails
      logger.error(f"AI parsing failed, using fallback: {e}")

  def test_connection(self) -> Dict[str, Any]:
    """Test the AI provider connection.
    Returns:
      The test connection result.
    """
    try:
      test_context = DebateContext(
          topic="Test Topic",
          bot_stance="Test position",
          message_count=1,
          user_message="Hello, can you introduce yourself?",
          conversation_history=[]
      )

      response = self.generate_response(test_context)

      return {
          'success': True,
          'provider': f"{self._provider_name.title()}Provider",
          'model': getattr(self, '_model', self._provider_name),
          'response': response[:100] + "..." if len(response) > 100 else response
      }

    except Exception as e:
      return {
          'success': False,
          'provider': f"{self._provider_name.title()}Provider",
          'error': str(e)
      }


# Global provider instance - initialized once per server execution
_ai_provider: Optional[DebateAIProvider] = None


def get_ai_provider() -> DebateAIProvider:
  """Get the global AI provider instance.
  Returns:
    The global AI provider instance.
  """
  global _ai_provider

  if _ai_provider is None:
    _ai_provider = DebateAIProvider()

  return _ai_provider


def test_ai_provider(provider_name: str = None) -> Dict[str, Any]:
  """Test the AI provider configuration.
  Args:
    provider_name: The name of the provider to test.
  Returns:
    The test connection result.
  """
  if provider_name:
    # Temporarily override the provider for testing
    original_provider = getattr(settings, 'AI_PROVIDER', 'openai')
    settings.AI_PROVIDER = provider_name

    # Force re-initialization for testing
    global _ai_provider
    _ai_provider = None

  try:
    provider = get_ai_provider()
    return provider.test_connection()

  except Exception as e:
    return {
        'success': False,
        'provider': provider_name or getattr(settings, 'AI_PROVIDER', 'openai'),
        'error': str(e)
    }
  finally:
    if provider_name:
      # Restore original provider and reset
      settings.AI_PROVIDER = original_provider
      _ai_provider = None
