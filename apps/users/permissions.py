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

from rest_framework import permissions


class IsCreationOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        创建用户无需 token
        """
        if not request.user.is_authenticated:
            if view.action == 'create':
                return True
            else:
                return False
        else:
            if view.action in ['list', 'retrieve', 'destroy']:
                if request.user.is_superuser:
                    return True
                else:
                    return False
            elif view.action in ['partial_update', 'update']:
                return True

    def has_object_permission(self, request, view, obj):
        if obj.username == request.user.username or (
                request.user.is_superuser
                and obj.merchant == request.user.merchant):
            return True
        else:
            return False


class IsOwn(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.username == request.user.username and obj.merchant == request.user.merchant:
            return True
        else:
            return False


class IsSuperuser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        else:
            return False
