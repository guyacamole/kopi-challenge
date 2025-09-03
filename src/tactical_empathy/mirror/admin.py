from django.contrib import admin
from .models import Conversation, Role, Message


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
  """Admin view for Role model."""
  list_display = ('name', 'created_at')
  list_filter = ('name', 'created_at')
  search_fields = ('name',)
  readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
  """Admin view for Conversation model."""
  list_display = ('topic', 'bot_stance', 'is_active', 'created_at', 'message_count')
  list_filter = ('is_active', 'created_at')
  search_fields = ('topic', 'bot_stance')
  readonly_fields = ('id', 'created_at', 'updated_at')
  date_hierarchy = 'created_at'

  def message_count(self, obj):
    return obj.messages.count()
  message_count.short_description = 'Messages'

  def get_queryset(self, request):
    return super().get_queryset(request).prefetch_related('messages')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
  """Admin view for Message model."""
  list_display = ('conversation_topic', 'role', 'content_preview', 'created_at')
  list_filter = ('role', 'created_at', 'conversation__is_active')
  search_fields = ('content', 'conversation__topic')
  readonly_fields = ('id', 'created_at')
  date_hierarchy = 'created_at'
  raw_id_fields = ('conversation', 'role')

  def conversation_topic(self, obj):
    return obj.conversation.topic[:50] + "..." if len(obj.conversation.topic) > 50 else obj.conversation.topic
  conversation_topic.short_description = 'Topic'

  def content_preview(self, obj):
    return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
  content_preview.short_description = 'Content'

  def get_queryset(self, request):
    return super().get_queryset(request).select_related('conversation', 'role')
