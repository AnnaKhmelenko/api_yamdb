import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Модели первого разработчика (аутентификация)
USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class CustomUser(AbstractUser):
    """Модификация пользователей."""
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    username = models.CharField(unique=True)
    first_name = models.CharField(blank=True)
    last_name = models.CharField(blank=True)
    bio = models.TextField(blank=True, null=True)
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
            self.confirmation_code = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


# Модели второго разработчика (категории, жанры, произведения)
class Category(models.Model):
    """Модель для категорий произведений"""
    name = models.CharField(
        max_length=50,
        verbose_name='Название категории',
        help_text='Введите название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug категории',
        help_text='Уникальный идентификатор категории для URL'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для жанров произведений"""
    name = models.CharField(
        max_length=50,
        verbose_name='Название жанра',
        help_text='Введите название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug жанра',
        help_text='Уникальный идентификатор жанра для URL'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений"""
    name = models.CharField(
        max_length=128,
        verbose_name='Название произведения',
        help_text='Введите название произведения'
    )
    year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(2050)
        ],
        verbose_name='Год выпуска',
        help_text='Введите год выпуска произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
        help_text='Выберите категорию произведения'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.year})'


class GenreTitle(models.Model):
    """Промежуточная модель для связи многие-ко-многим"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='genre_links',
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='title_links',
        verbose_name='Жанр'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre'
            )
        ]

    def __str__(self):
        return f'{self.title} - {self.genre}'
