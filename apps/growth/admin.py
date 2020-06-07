from django.contrib import admin

from .models import Checkin, Invite, Log


@admin.register(Checkin)
class CheckinAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'from_points',
        'to_points',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'left',
        'shortuuid',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'invite',
        'to_user',
        'desc',
        'created_at',
        'updated_at',
    )
    list_filter = ('created_at', )
    readonly_fields = ["created_at", 'updated_at']
    date_hierarchy = 'created_at'
