from rest_framework import permissions


class IsSuperuserPatch(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'partial_update':
            if request.user.is_superuser:
                return True
            else:
                return False
        else:
            return True


class IsOwnOrSuperuser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            if obj.user == request.user or (request.user.is_superuser and obj.merchant == request.user.merchant):
                return True
            else:
                return False
        elif hasattr(obj, 'transaction'):
            if obj.transaction.user == request.user or (request.user.is_superuser and obj.merchant == request.user.merchant):
                return True
        else:
            return False


class IsOwn(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            if obj.user == request.user and obj.merchant == request.user.merchant:
                return True
            else:
                return False
        elif hasattr(obj, 'transaction'):
            if obj.transaction.user == request.user and obj.merchant == request.user.merchant:
                return True
        else:
            return False


class IsSuperuser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser and obj.merchant == request.user.merchant:
            return True
        else:
            return False
