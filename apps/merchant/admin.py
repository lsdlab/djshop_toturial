from django.contrib import admin

from .models import Merchant


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'remark',
        'mobile',
        'deleted',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'created_at',
        'updated_at',
    )
    search_fields = ('name', 'remark', 'mobile')
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
