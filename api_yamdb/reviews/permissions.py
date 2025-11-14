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
        # Чтение разрешено для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Запись только для админов
        return request.user and request.user.is_staff


class IsModeratorOrAuthor(permissions.BasePermission):
    """
    Разрешение для модераторов, авторов и админов.

    Чтение разрешено всем, редактирование - только указанным ролям.
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Проверяем аутентификацию
        if not request.user or not request.user.is_authenticated:
            return False

        # Редактирование разрешено для:
        # - Админов (is_staff)
        # - Модераторов
        # - Авторов объекта
        return (
            request.user.is_staff
            or getattr(request.user, 'is_moderator', False)
            or obj.author == request.user
        )


class IsAdminOnly(permissions.BasePermission):
    """Разрешение только для администраторов."""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешение для владельца объекта или администратора."""

    def has_object_permission(self, request, view, obj):
        # Для безопасных методов разрешаем доступ
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для изменения/удаления проверяем права
        if not request.user or not request.user.is_authenticated:
            return False

        return obj.author == request.user or request.user.is_staff
