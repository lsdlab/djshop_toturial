from django.contrib import admin

from .models import SearchHistory, BrowserHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'keyword', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(BrowserHistory)
class BrowserHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'user',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
