from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):
    """Разрешение только для администраторов и суперпользователей."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на запись только для администраторов.
    Остальные могут только читать.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and request.user.is_admin
            )
        )


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение для авторов, модераторов, администраторов.
    Чтение разрешено всем, редактирование - только указанным ролям.
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Редактирование разрешено для:
        # - Администраторов
        # - Модераторов
        # - Авторов объекта
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user
            )
        )
