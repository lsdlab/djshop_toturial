from django.contrib import admin

from .models import Express


@admin.register(Express)
class ExpressAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'transaction', 'shipper_info_provider',
                    'shipper_code', 'shipper_name', 'shipper', 'sn',
                    'created_at', 'updated_at')
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
