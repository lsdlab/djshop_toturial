from rest_framework import permissions


class IsSuperuserCreatePatch(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'patch']:
            if request.user.is_superuser:
                return True
            else:
                return False
        else:
            return True


class IsOwn(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            if obj.user == request.user and obj.merchant == request.user.merchant:
                return True
            else:
                return False
        else:
            return False


class IsSuperuser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser and obj.merchant == request.user.merchant:
            return True
        else:
            return False
