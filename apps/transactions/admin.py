from django.contrib import admin

from .models import Transaction, TransactionProduct, Invoice, Refund, Collect


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'user',
        'sn',
        'status',
        'payment',
        'deal_type',
        'express_type',
        'note',
        'total_amount',
        'expired_datetime',
        'seller_packaged_datetime',
        'received_datetime',
        'payment_sn',
        'payment_datetime',
        'promotion',
        'paid',
        'closed_datetime',
        'review_datetime',
        'address',
        'coupon_log',
        'seller_note',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'created_at',
        'updated_at',
        'status',
        'payment',
        'deal_type',
        'express_type',
    )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(TransactionProduct)
class TransactionProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction',
        'product_spec',
        'nums',
        'price',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'type',
        'transaction',
        'title',
        'price',
        'company_tax_sn',
        'shipped',
        'shipped_datetime',
        'issued',
        'issued_datetime',
        'address',
        'note',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'shipped',
        'issued',
        'created_at',
        'updated_at',
    )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'transaction',
        'transaction_product',
        'sn',
        'refund_price',
        'note',
        'refund_type',
        'auditor',
        'audit',
        'audit_datetime',
        'audit_note',
        'shipper',
        'shipper_sn',
        'refund_enter_ship_info_datetime',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'audit_datetime',
        'created_at',
        'updated_at',
    )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction',
        'store',
        'name',
        'mobile',
        'pickup_datetime',
        'note',
        'picked',
        'picked_datetime',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'pickup_datetime',
        'picked',
        'picked_datetime',
        'created_at',
        'updated_at',
    )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
