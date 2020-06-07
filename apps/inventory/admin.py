from django.contrib import admin

from .models import Stock, ReplenishLog


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'desc',
        'nums',
        'merchant',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'


@admin.register(ReplenishLog)
class ReplenishLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'nums',
        'note',
        'user',
        'merchant',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name',)
    date_hierarchy = 'created_at'
