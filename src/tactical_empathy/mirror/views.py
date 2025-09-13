from .conversations_view import ConversationAPIView
from .debate_view import DebateAPIViewPost, DebateAPIView
from .messages_view import MessagesAPIViewPost, MessagesAPIView
from .conversations_view import ConversationAPIViewWithId
conversation_api = ConversationAPIView.as_view()
conversation_api_with_id = ConversationAPIViewWithId.as_view()
debate_api = DebateAPIView.as_view()
debate_api_post = DebateAPIViewPost.as_view()
messages_api = MessagesAPIView.as_view()
messages_api_post = MessagesAPIViewPost.as_view()
