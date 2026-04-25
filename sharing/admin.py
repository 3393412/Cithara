from django.contrib import admin
from .models import ShareLink

@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ('token', 'song', 'shared_by', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('token', 'song__title', 'shared_by__username')
    readonly_fields = ('token', 'created_at')
