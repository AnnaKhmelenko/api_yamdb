import uuid
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя с расширенными полями.

    Наследует от AbstractUser и добавляет поля для ролей,
    биографии и кода подтверждения.
    """
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Биография',
        help_text='Расскажите о себе'
    )
    email = models.EmailField(
        'Email',
        unique=True,
        db_index=True,
        help_text='Укажите электронную почту'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        max_length=32,
        blank=True,
        null=True,
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
        return self.role == ADMIN or self.is_staff

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == MODERATOR

    @property
    def is_user(self):
        """Проверяет, является ли пользователь обычным пользователем."""
        return self.role == USER

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username


class Category(models.Model):
    """Модель категории произведений."""

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
        """Возвращает строковое представление категории."""
        return self.name


class Genre(models.Model):
    """Модель жанра произведений."""

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
        """Возвращает строковое представление жанра."""
        return self.name


class Title(models.Model):
    """Модель произведения (фильмы, книги, музыка и т.д.)."""

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
    description = models.TextField(
        blank=True,
        null=True,
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
        through='GenreTitle',
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

    def clean(self):
        """Проверяет корректность года выпуска."""
        if self.year > datetime.now().year:
            raise ValidationError(
                {'year': 'Год выпуска не может быть в будущем'}
            )

    def save(self, *args, **kwargs):
        """Сохраняет произведение с предварительной валидацией."""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def rating(self):
        """Вычисляет средний рейтинг произведения на основе отзывов."""
        from django.db.models import Avg

        # Используем правильный related_name 'reviews' из модели Review
        avg_rating = self.reviews.aggregate(Avg('score'))['score__avg']

        # Если есть рейтинг - округляем и возвращаем, иначе None
        return round(avg_rating) if avg_rating is not None else None

    def __str__(self):
        """Возвращает строковое представление произведения."""
        return f'{self.name} ({self.year})'


class GenreTitle(models.Model):
    """
    Промежуточная модель для связи Many-to-Many между Title и Genre.

    Позволяет добавлять дополнительные поля к связи в будущем.
    """

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
        verbose_name = 'Связь жанра и произведения'
        verbose_name_plural = 'Связи жанров и произведений'
        indexes = [
            models.Index(fields=['title', 'genre']),
        ]

    def __str__(self):
        """Возвращает строковое представление связи."""
        return f'{self.title} - {self.genre}'


class Review(models.Model):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
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
    text = models.TextField(verbose_name='Текст комментария')
    author = models.ForeignKey(
        CustomUser,
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
