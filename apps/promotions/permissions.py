from rest_framework import permissions


class IsSuperuserCreateUpdate(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'partial_update']:
            if request.user.is_superuser:
                return True
            else:
                return False
        else:
            return True


class IsOwn(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user and obj.merchant == request.user.merchant:
            return True
        else:
            return False
