import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    email = models.EmailField('Email', unique=True)
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        max_length=36,
        blank=True,
        null=True,
        verbose_name='Код подтверждения',
        help_text='Код подтверждения для регистрации'
    )

    def save(self, *args, **kwargs):
        if not self.confirmation_code:
            # Генерируем новый код, если его еще нет
            self.confirmation_code = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
