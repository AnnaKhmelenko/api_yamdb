from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ пользователю или гостю только к GET/OPTIONS/HEAD."""

    def has_permission(self, request, view):
        """Проверка на запросы к объекту
        Для безопасных методов всегда True."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin)


class IsAdminUser(permissions.BasePermission):
    """Доступ только для пльзователей с ролью АДМИНА или СУПЕРЮЗЕРА."""

    def has_permission(self, request, view):
        return request.user.is_admin


class IsAuthorOrModerAdminOnly(permissions.BasePermission):
    """Доступ гостю, пользователю только к GET/OPTIONS/HEAD."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_moderator
                or request.user == obj.author
            )
        )
