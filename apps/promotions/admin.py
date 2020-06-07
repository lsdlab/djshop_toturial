from django.contrib import admin

from .models import (ProductPromotion, Promotion, Log)


@admin.register(ProductPromotion)
class ProductPromotionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'promotion_type',
        'product_spec',
        'original_sale_price',
        'sold',
        'deleted',
        'merchant',
        'bargain_start_price',
        'bargain_end_price',
        'bargain_percent_range',
        'promotion_price',
        'promotion_stock',
        'groupon_limit',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'promotion_type',
        'promotion_product',
        'current_price',
        'start_datetime',
        'end_datetime',
        'shortuuid',
        'dealed',
        'transaction_created',
        'merchant',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'start_datetime',
        'end_datetime',
        'dealed',
        'transaction_created',
        'created_at',
        'updated_at',
    )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'promotion',
        'user',
        'bargain_from_price',
        'bargain_to_price',
        'bargain_discount',
        'merchant',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
