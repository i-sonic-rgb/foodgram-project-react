from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    '''Custom permission class for Recipe ViewSet.'''
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and obj.author == request.user
            or request.user.is_authenticated and request.user.is_admin
            or request.user.is_authenticated and not request.user.is_blocked
            or request.user.is_authenticated and request.user.is_superuser
        )
