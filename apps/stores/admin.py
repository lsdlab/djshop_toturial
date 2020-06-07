from django.contrib import admin

from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'address',
        'open_datetime',
        'contact',
        'remark',
        'deleted',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    search_fields = ('name', 'address', 'contact', 'remark')
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
