from rest_framework import permissions


class IsSuperuserCreate(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'partial_update', 'destroy']:
            if request.user.is_superuser:
                return True
            else:
                return False
        else:
            return True


class IsSuperuser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser and obj.merchant == request.user.merchant:
            return True
        else:
            return False
