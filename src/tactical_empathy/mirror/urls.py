from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Web interface
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('list/', views.list_conversations, name='list'),
    path('<uuid:id>/', views.detail, name='detail'),
    # API endpoint for the chatbot challenge
    path('api/chat/', api_views.chatbot_api, name='chatbot_api'),
]
