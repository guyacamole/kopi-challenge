from django.urls import path
from . import views, views_web
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    # API endpoints
    path('conversation/', views.conversation_api, name='conversation_api'),
    path('conversation/<conversation_id>/', views.conversation_api_with_id, name='conversation_api_with_id'),
    path('debate/', views.debate_api_post, name='debate_api_post'),
    path('debate/<conversation_id>/', views.debate_api, name='debate_api'),
    path('messages/<message_id>/', views.messages_api, name='messages_api'),
    path('messages/', views.messages_api_post, name='messages_api_post'),
    # API schema and documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # Web interface endpoints
    path('web/', views_web.index, name='index'),
    path('web/create/', views_web.create, name='create'),
    path('web/list/', views_web.list_conversations, name='list'),
    path('web/conversation/<str:id>/', views_web.detail, name='detail'),
]
