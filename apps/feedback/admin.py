from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'type',
        'user',
        'product_spec',
        'transaction_product',
        'content',
        'solved',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
