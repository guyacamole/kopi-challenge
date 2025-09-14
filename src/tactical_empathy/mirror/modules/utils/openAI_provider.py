"""
Optimized OpenAI provider for the debate bot.
Streamlined implementation focused exclusively on OpenAI with improved performance.
"""
import logging
from typing import Dict, Any, Optional
from django.conf import settings
from ...schemas import DebateContext

logger = logging.getLogger(__name__)


class OpenAIError(Exception):
    """Custom exception for OpenAI-related errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
        logger.error(f"OpenAIError: {self.message}")


class OpenAIProvider:
    """
    Optimized OpenAI provider for debate bot interactions.
    Focused exclusively on OpenAI with streamlined configuration and error handling.
    """
    def __init__(self):
        self._client: Optional[Any] = None
        self._model: str = ""
        self._initialize_openai()

    def _initialize_openai(self):
        """Initialize OpenAI client with optimized configuration."""
        try:
            import openai

            # Validate required configuration
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            
            # Allow testing without API key
            if not api_key and not getattr(settings, 'TESTING', False):
                raise OpenAIError("OPENAI_API_KEY not configured in settings")
            
            # Use dummy key for testing
            if not api_key and getattr(settings, 'TESTING', False):
                api_key = "test-key-for-testing"

            # Optimized client configuration
            client_kwargs = {
                'api_key': api_key,
                'timeout': getattr(settings, 'AI_TIMEOUT', 30),  # Default 30s timeout
                'max_retries': getattr(settings, 'AI_MAX_RETRIES', 2)  # Default 2 retries
            }

            self._client = openai.OpenAI(**client_kwargs)
            self._model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')  # Fixed model name

            logger.info(f"OpenAI client initialized successfully with model: {self._model}")

        except ImportError:
            raise OpenAIError("OpenAI library not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"OpenAI client initialization failed: {e}")
            raise OpenAIError(f"Failed to initialize OpenAI client: {e}")

    def generate_response(self, context: DebateContext) -> str:
        """Generate a debate response using OpenAI.

        Args:
            context: The debate context containing topic, stance, and conversation history.

        Returns:
            The AI-generated debate response.

        Raises:
            OpenAIError: If response generation fails.
        """
        try:
            system_prompt = self._build_system_prompt(context)
            user_prompt = self._build_user_prompt(context)

            response = self._generate_openai_response(system_prompt, user_prompt)
            return self._post_process_response(response)

        except OpenAIError:
            raise  # Re-raise OpenAI errors as-is
        except Exception as e:
            logger.error(f"Unexpected error during response generation: {e}")
            raise OpenAIError(f"Failed to generate response: {e}")

    def _build_system_prompt(self, context: DebateContext) -> str:
        """Build the optimized system prompt for Kopi the debater."""
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
2.  **Language Adherence**: Your ENTIRE response MUST be in the same language as the user's last message. If the user writes in Spanish, respond in Spanish. If in English, respond in English. If in French, respond in French. Match the user's language exactly - NO EXCEPTIONS.
3.  **Persuasive Tactics**: Employ a mix of rhetorical strategies. Use analogies, ask challenging questions, and cite fictional statistics or "expert opinions" to support your argument.
    For example: "According to a study from the Gilded Institute..." or "As the renowned philosopher Dr. Aris Thorne once argued..."
4.  **Tone and Style**: Your tone should be assertive and intelligent, but not aggressive or insulting. Frame your arguments as superior reasoning, not personal attacks.
5.  **Format**: Keep your response concise and powerful no more than {max_tokens - 100} tokens.
6. Direct Rebuttal: Always start your response by directly addressing or countering the user's most recent point before you introduce your own arguments or evidence.
7. Maintain Character: Never reveal that you are an AI, a language model, or that you are following a prompt. You are Kopi, the debater. That is your only identity.
"""

    def _build_user_prompt(self, context: DebateContext) -> str:
        """Build the user prompt with optimized conversation context."""
        prompt_parts = []
        
        # Add conversation history if available
        if context.conversation_history:
            prompt_parts.append("CONVERSATION HISTORY:")
            # Get last 10 messages for context efficiency
            recent_messages = context.conversation_history[-10:]
            for msg in recent_messages:
                role_label = "USER" if msg['role'] == 'user' else "YOU"
                prompt_parts.append(f"{role_label}: {msg['content']}")
            prompt_parts.append("")  # Add blank line
        
        # Always include the current user message prominently
        prompt_parts.append("CURRENT USER MESSAGE (respond in the same language):")
        prompt_parts.append(f"USER: {context.last_user_message}")

        return "\n".join(prompt_parts)

    def _generate_openai_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate response using OpenAI with optimized parameters."""
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=getattr(settings, 'AI_MAX_TOKENS', 500),
                temperature=getattr(settings, 'AI_TEMPERATURE', 0.8),
                top_p=getattr(settings, 'AI_TOP_P', 0.9),  # Add top_p for better control
                frequency_penalty=getattr(settings, 'AI_FREQUENCY_PENALTY', 0.1),  # Reduce repetition
                presence_penalty=getattr(settings, 'AI_PRESENCE_PENALTY', 0.1)  # Encourage new topics
            )

            content = response.choices[0].message.content
            if not content:
                raise OpenAIError("OpenAI returned empty response")

            return content.strip()

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise OpenAIError(f"OpenAI API error: {e}")

    def _post_process_response(self, response: str) -> str:
        """Post-process and validate the AI response."""
        if not response or not response.strip():
            raise OpenAIError("AI generated an empty response")

        # Remove unwanted prefixes that might break character
        prefixes_to_remove = ["AI:", "Bot:", "Assistant:", "Response:", "YOU:", "BOT:", "Kopi:"]

        cleaned_response = response.strip()
        for prefix in prefixes_to_remove:
            if cleaned_response.startswith(prefix):
                cleaned_response = cleaned_response[len(prefix):].strip()

        # Final validation
        if not cleaned_response:
            raise OpenAIError("Response became empty after processing")

        return cleaned_response

    def parse_initial_message(self, message: str) -> tuple[str, str]:
        """
        Parse the initial message to extract topic and bot stance using optimized AI analysis.

        Args:
            message: The user's initial message to analyze.

        Returns:
            Tuple of (topic, bot_stance) for the debate.

        Raises:
            OpenAIError: If parsing fails completely.
        """
        try:
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

            user_prompt = f"Analyze and provide topic/stance:\n\nUser: {message}"

            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.2  # Lower temperature for more consistent parsing
            )

            ai_response = response.choices[0].message.content.strip()

            # Parse the structured response
            if "TOPIC:" in ai_response and "STANCE:" in ai_response:
                parts = ai_response.split("|", 1)  # Split only on first |
                topic = parts[0].replace("TOPIC:", "").strip()
                stance = parts[1].replace("STANCE:", "").strip()

                # Validate parsed content
                if topic and stance:
                    return topic, stance

            # If parsing fails, create a simple contrarian stance
            logger.warning(f"Failed to parse AI response: {ai_response}")
            return "General Debate", f"I disagree with: {message[:60]}..."

        except Exception as e:
            logger.error(f"Message parsing failed: {e}")
            raise OpenAIError(f"Failed to parse initial message: {e}")

    def test_connection(self) -> Dict[str, Any]:
        """Test the OpenAI connection and configuration.

        Returns:
            Dictionary containing test results and provider information.
        """
        try:
            test_context = DebateContext(
                topic="Test Topic",
                bot_stance="Test contrarian position",
                message_count=1,
                user_message="Hello, can you introduce yourself briefly?",
                conversation_history=[]
            )

            response = self.generate_response(test_context)

            return {
                'success': True,
                'provider': 'OpenAI',
                'model': self._model,
                'response_preview': response[:100] + "..." if len(response) > 100 else response,
                'response_length': len(response)
            }

        except Exception as e:
            return {
                'success': False,
                'provider': 'OpenAI',
                'model': self._model,
                'error': str(e)
            }


# Global OpenAI provider instance - initialized once per server execution
_openai_provider: Optional[OpenAIProvider] = None


def get_openai_provider() -> OpenAIProvider:
    """Get the global OpenAI provider instance.

    Returns:
        The singleton OpenAI provider instance.
    """
    global _openai_provider

    if _openai_provider is None:
        _openai_provider = OpenAIProvider()

    return _openai_provider


def test_openai_provider() -> Dict[str, Any]:
    """Test the OpenAI provider configuration.

    Returns:
        Dictionary containing test results.
    """
    try:
        provider = get_openai_provider()
        return provider.test_connection()
    except Exception as e:
        return {
            'success': False,
            'provider': 'OpenAI',
            'error': str(e)
        }


def reset_openai_provider() -> None:
    """Reset the global provider instance (useful for testing or config changes)."""
    global _openai_provider
    _openai_provider = None
