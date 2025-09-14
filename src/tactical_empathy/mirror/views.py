from .view_conversations  import ConversationAPIView, ConversationAPIViewWithId
from .view_debate import DebateAPIViewPost, DebateAPIView
from .view_messages import MessagesAPIViewPost, MessagesAPIView 
conversation_api = ConversationAPIView.as_view()
conversation_api_with_id = ConversationAPIViewWithId.as_view()
debate_api = DebateAPIView.as_view()
debate_api_post = DebateAPIViewPost.as_view()
messages_api = MessagesAPIView.as_view()
messages_api_post = MessagesAPIViewPost.as_view()
