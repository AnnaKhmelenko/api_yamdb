from rest_framework.permissions import BasePermission, IsAuthenticated

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in ('GET', 'HEAD', 'OPTIONS') or
            request.user and request.user.is_superuser
        )

class IsModeratorOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # владелец или модератор или администратор
        return (
            request.method in ('GET', 'HEAD') or
            request.user.is_superuser or
            request.user.role == 'moderator' or
            obj.author == request.user
        )