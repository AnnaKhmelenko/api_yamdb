import re
import uuid
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

from .constants import (
    ADMIN, MAX_LENGTH_CATEGORY_NAME,
    MAX_LENGTH_CATEGORY_SLUG, MAX_LENGTH_COMMENT_TEXT,
    MAX_LENGTH_CONFIRMATION_CODE, MAX_LENGTH_EMAIL,
    MAX_LENGTH_REVIEW_TEXT, MAX_LENGTH_TITLE_NAME,
    MAX_LENGTH_USERNAME, MAX_SCORE, MIN_SCORE, MODERATOR,
    ROLE_CHOICES, USER)


def validate_username(value):
    """Валидация имени пользователя."""
    if value.lower() == 'me':
        raise ValidationError('Имя пользователя "me" не разрешено.')

    invalid_chars = re.sub(r'[\w.@+-]', '', value)
    if invalid_chars:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: {invalid_chars}'
        )
    return value


def validate_year(value):
    """Валидация года выпуска."""
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError('Год выпуска не может быть в будущем.')
    return value


class BaseSlugModel(models.Model):
    """Абстрактная базовая модель для категорий и жанров."""

    name = models.CharField(
        max_length=MAX_LENGTH_CATEGORY_NAME,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_CATEGORY_SLUG,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Модель пользователя с расширенными полями.
    """

    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимые символы в имени пользователя.'
            ),
            validate_username
        ]
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография',
        help_text='Расскажите о себе'
    )
    email = models.EmailField(
        'Email',
        unique=True,
        max_length=MAX_LENGTH_EMAIL,
        help_text='Укажите электронную почту'
    )
    role = models.CharField(
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        max_length=MAX_LENGTH_CONFIRMATION_CODE,
        blank=True,
        verbose_name='Код подтверждения',
        help_text='Код подтверждения для регистрации'
    )

    def save(self, *args, **kwargs):
        """Сохраняет пользователя, генерирует код подтверждения если надо."""
        if not self.confirmation_code:
            self.confirmation_code = uuid.uuid4().hex
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == MODERATOR

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username


class Category(BaseSlugModel):
    """Модель категории произведений."""

    class Meta(BaseSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseSlugModel):
    """Модель жанра произведений."""

    class Meta(BaseSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения (фильмы, книги, музыка и т.д.)."""

    name = models.CharField(
        max_length=MAX_LENGTH_TITLE_NAME,
        verbose_name='Название произведения',
        help_text='Введите название произведения'
    )
    year = models.SmallIntegerField(
        validators=[validate_year],
        verbose_name='Год выпуска',
        help_text='Введите год выпуска произведения'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание произведения',
        help_text='Введите описание произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория',
        help_text='Выберите категорию произведения'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанр',
        help_text='Выберите жанр произведения'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'year']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        """Возвращает строковое представление произведения."""
        return f'{self.name} ({self.year})'


class Review(models.Model):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        max_length=MAX_LENGTH_REVIEW_TEXT,
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(MIN_SCORE),
            MaxValueValidator(MAX_SCORE)
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]
        indexes = [
            models.Index(fields=['title', 'pub_date']),
            models.Index(fields=['author', 'pub_date']),
        ]

    def __str__(self):
        """Возвращает строковое представление отзыва."""
        return f'{self.author.username}: {self.text[:30]}...'


class Comment(models.Model):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(
        max_length=MAX_LENGTH_COMMENT_TEXT,
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']
        indexes = [
            models.Index(fields=['review', 'pub_date']),
        ]

    def __str__(self):
        """Возвращает строковое представление комментария."""
        return f'{self.author.username}: {self.text[:30]}...'
