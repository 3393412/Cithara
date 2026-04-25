from django.contrib import admin
from .models import Song, GenerationJob

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'genre', 'mood', 'vocal', 'create_at')
    list_filter = ('genre', 'mood', 'vocal')
    search_fields = ('title', 'user__username', 'prompt')

@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'provider', 'status', 'title', 'created_at')
    list_filter = ('status', 'provider')
    search_fields = ('title', 'user__username', 'task_id')
    readonly_fields = ('task_id', 'provider', 'raw_response', 'created_at', 'updated_at')
