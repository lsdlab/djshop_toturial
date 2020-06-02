from django.contrib import admin

from .models import Notice, Banner, Splash


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'link',
        'header_image',
        'deleted',
        'sent',
        'sent_datetime',
        'merchant',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'banner',
        'status',
        'display_order',
        'product',
        'merchant',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Splash)
class SplashAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'splash', 'status', 'link', 'product',
                    'merchant', 'created_at', 'updated_at')
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
