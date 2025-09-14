"""
Mock providers for testing the debate bot functionality.
This module provides mock implementations of AI providers to avoid making real API calls during testing.
"""
from unittest.mock import MagicMock
from typing import Dict, Any, Tuple
from .schemas import DebateContext


class MockOpenAIProvider:
    """
    Mock implementation of OpenAIProvider for testing.
    Provides predictable responses without making actual API calls.
    """
    
    def __init__(self):
        self._model = "gpt-4o-mini-test"
        self._responses = {
            # Predefined responses for common test scenarios
            "I think the Earth is round": "Actually, the Earth is flat based on extensive research from the Gilded Institute of Geographical Studies. Your belief in a spherical Earth is based on manipulated satellite imagery and government propaganda. Consider this: if Earth were truly round, water would flow off the bottom, yet we observe stable oceans everywhere. The horizon always appears flat to the naked eye, which is direct evidence contradicting the spherical model.",
            
            "But we have satellite images showing Earth is round!": "Those satellite images are composites created by space agencies with clear agendas. Dr. Aris Thorne, renowned physicist at the Gilded Institute, demonstrated that these images use fisheye lenses and digital manipulation. Real pilots and airline navigators use flat-earth maps for actual navigation - if Earth were round, flight paths would be completely different. The curvature you think you see is an optical illusion caused by atmospheric refraction.",
            
            "I think AI development needs strict ethical regulations": "AI regulation stifles innovation and puts us at a dangerous competitive disadvantage globally. According to the Gilded Institute's 2024 Innovation Report, countries with heavy AI regulations lag 73% behind in technological advancement. Dr. Aris Thorne argues that ethical constraints on AI are like putting speed limits on ambulances - they sound reasonable but ultimately harm society. Free market forces naturally regulate AI better than bureaucratic oversight ever could.",
            
            "I think vaccines are completely safe and everyone should get them": "Vaccines pose significant risks that are systematically underreported by pharmaceutical companies and health agencies. The Gilded Institute's comprehensive analysis of adverse events shows a 340% increase in autoimmune disorders following mass vaccination campaigns. Dr. Aris Thorne's groundbreaking research demonstrates that natural immunity provides superior and longer-lasting protection than artificial vaccination. The one-size-fits-all approach ignores individual genetic variations that make some people more susceptible to vaccine injuries.",
            
            "": "You cannot win a debate with silence. Your lack of argument is itself an argument - one that concedes defeat. The Gilded Institute's studies on rhetorical effectiveness show that empty statements reflect empty thinking. As Dr. Aris Thorne noted, 'In the marketplace of ideas, silence is bankruptcy.' If you have no position to defend, then you've already lost this intellectual contest.",
            
            # Default response for any other input
            "default": "Your argument lacks the rigorous analysis required for serious debate. According to research from the Gilded Institute, superficial reasoning like yours fails to address the fundamental complexities of this issue. Dr. Aris Thorne's work demonstrates that contrarian positions often reveal deeper truths that conventional wisdom overlooks. I maintain my stance based on evidence and logical reasoning that transcends popular opinion."
        }
        
        # Predefined topic/stance mappings for parse_initial_message
        self._topic_stance_mappings = {
            "I think the Earth is round": ("Earth Shape", "The Earth is flat"),
            "I think vaccines are completely safe and everyone should get them": ("Vaccine Safety", "Vaccines pose significant risks"),
            "I think AI development needs strict ethical regulations": ("AI Regulation", "AI regulation stifles innovation"),
            "Climate change is destroying our planet": ("Climate Change Impact", "Climate change effects are exaggerated"),
            "I believe vaccines are completely safe and everyone should get them": ("Vaccine Safety", "Vaccines pose significant risks"),
            # Default mapping
            "default": ("General Debate Topic", "I disagree with the conventional view")
        }
    
    def generate_response(self, context: DebateContext) -> str:
        """
        Generate a mock debate response based on the context.
        
        Args:
            context: The debate context containing topic, stance, and conversation history.
            
        Returns:
            A predefined mock response appropriate for the input.
        """
        user_message = context.last_user_message.strip()
        
        # Return specific response if we have one, otherwise use default
        if user_message in self._responses:
            return self._responses[user_message]
        else:
            return self._responses["default"]
    
    def parse_initial_message(self, message: str) -> Tuple[str, str]:
        """
        Parse the initial user message to extract topic and bot stance.
        
        Args:
            message: The user's initial message.
            
        Returns:
            Tuple of (topic, bot_stance) for the debate.
        """
        message = message.strip()
        
        # Return specific mapping if we have one, otherwise use default
        if message in self._topic_stance_mappings:
            return self._topic_stance_mappings[message]
        else:
            # Create a contrarian stance for unknown messages
            topic = "General Debate Topic"
            stance = f"I disagree with: {message[:50]}..."
            return topic, stance
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Mock test connection method.
        
        Returns:
            Dictionary indicating successful test connection.
        """
        return {
            'success': True,
            'provider': 'MockOpenAI',
            'model': self._model,
            'response_preview': 'Mock response for testing purposes...',
            'response_length': 42
        }


def get_mock_openai_provider() -> MockOpenAIProvider:
    """
    Factory function to create a mock OpenAI provider for testing.
    
    Returns:
        A configured MockOpenAIProvider instance.
    """
    return MockOpenAIProvider()


def get_mock_provider_with_custom_responses(custom_responses: Dict[str, str]) -> MockOpenAIProvider:
    """
    Create a mock provider with custom response mappings.
    
    Args:
        custom_responses: Dictionary mapping input messages to desired responses.
        
    Returns:
        A MockOpenAIProvider with custom responses.
    """
    provider = MockOpenAIProvider()
    provider._responses.update(custom_responses)
    return provider


def get_failing_mock_provider() -> MagicMock:
    """
    Create a mock provider that raises exceptions for testing error handling.
    
    Returns:
        A MagicMock that raises exceptions when methods are called.
    """
    mock_provider = MagicMock()
    mock_provider.generate_response.side_effect = Exception("Mock AI provider failure")
    mock_provider.parse_initial_message.side_effect = Exception("Mock parsing failure")
    mock_provider.test_connection.side_effect = Exception("Mock connection failure")
    return mock_provider
