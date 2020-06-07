from rest_framework import permissions


class IsTopicSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'partial_update', 'destroy']:
            if request.user.is_superuser:
                return True
            else:
                return False
        else:
            return True
