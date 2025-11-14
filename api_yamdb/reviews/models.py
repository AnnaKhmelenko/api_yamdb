from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserRoles(models.TextChoices):
    """Роли пользователей на проекте."""

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class UserManagerYaMDB(UserManager):
    """Класс определения суперпользователя - АДМИН."""

    def create_superuser(self, username, email=None,
                         password=None, **extra_fields):
        extra_fields.setdefault('role', UserRoles.ADMIN)
        return super().create_superuser(username, email,
                                        password, **extra_fields)


class CustomUser(AbstractUser):
    """Кастомный пользователь. (Расширенная модель)"""

    username = models.CharField(unique=True)
    bio = models.TextField(blank=True, verbose_name='Биография', null=True)
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='E-mail',
    )
    role = models.CharField(
        max_length=9,
        choices=UserRoles.choices,
        default=UserRoles.USER,
        verbose_name='Роль',
    )
    confirmation_code = models.CharField(
        max_length=36,
        blank=True,
        null=True,
        verbose_name='Код подтверждения',
        help_text='Код подтверждения для регистрации'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def str(self):
        return self.username

    @property
    def is_admin(self):
        return (
            self.role == UserRoles.ADMIN
            or self.is_staff
            or self.is_superuser
        )

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR
