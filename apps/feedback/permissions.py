from rest_framework import permissions


class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['partial_update']:
            if request.user.is_superuser:
                return True
            else:
                return False
        else:
            return True
