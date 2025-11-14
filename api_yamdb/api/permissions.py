from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение только для администраторов и суперпользователей."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.role == 'admin' or request.user.is_superuser)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение на запись только для администраторов."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and (request.user.role == 'admin' or request.user.is_superuser)
            )
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешение на редактирование только для автора объекта."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsModeratorOrAuthor(permissions.BasePermission):
    """Разрешение для модераторов, администраторов и авторов объекта."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and (
                    request.user.role in ('moderator', 'admin')
                    or request.user.is_superuser
                    or obj.author == request.user
                )
            )
        )
