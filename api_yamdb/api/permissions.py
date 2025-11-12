from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только для автора.
    Остальные могут только читать.
    """
    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Редактирование только для автора
        return obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только для админов.
    Остальные могут только читать.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )


class IsModeratorOrAuthor(permissions.BasePermission):
    """
    Разрешение для модераторов и авторов.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or obj.author == request.user
        )