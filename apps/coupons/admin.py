from django.contrib import admin

from .models import Coupon, CouponLog


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'type',
        'internal_type',
        'name',
        'desc',
        'category',
        'product',
        'reach_price',
        'reach_unit',
        'discount_price',
        'start_datetime',
        'end_datetime',
        'total',
        'left',
        'points',
        'outdated',
        'in_use',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'created_at',
        'updated_at',
        'start_datetime',
        'end_datetime',
        'outdated',
    )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(CouponLog)
class CouponLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'coupon',
        'user',
        'used',
        'used_datetime',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'created_at',
        'updated_at',
        'used',
        'used_datetime',
    )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
