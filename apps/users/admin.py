"""
  (c) Copyright JC 2018-2020 All Rights Reserved
  -----------------------------------------------------------------------------
  File Name    :
  Description  :
  Author       : JC
  Email        : lsdvincent@gmail.com
  GiitHub      : https://github.com/lsdlab
  -----------------------------------------------------------------------------
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    list_display = ('id', 'mobile', 'email', 'username', 'nickname',
                    'merchant', 'is_superuser', 'is_staff', 'is_active',
                    'deleted', 'date_joined')
    search_fields = (
        'mobile',
        'email',
        'username',
        'nickname',
    )
    list_filter = ('date_joined', 'is_superuser', 'is_staff', 'is_active',
                   'deleted')
    date_hierarchy = 'date_joined'

    fieldsets = AuthUserAdmin.fieldsets + ((None, {
        'fields': ('mobile', 'avatar', 'nickname', 'merchant')
    }), )
