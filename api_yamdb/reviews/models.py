from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Модель для категорий произведений, содержит id, name, slug."""
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
        """Строковое представление объекта категории."""
        return self.name


class Genre(models.Model):
    """Модель для жанров произведений, содержит id, name, slug."""
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
        """Строковое представление объекта жанра."""
        return self.name


class Title(models.Model):
    """Модель для произведений (фильмы, книги, музыка).

    Cодержит id, name, year, category
        name (CharField): Название произведения.
        year (IntegerField): Год выпуска.
        category (ForeignKey): Связь с категорией.
    """
    name = models.CharField(
        max_length=128,
        verbose_name='Название произведения',
        help_text='Введите название произведения'
    )
    year = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1000),  # Минимальный год
            MaxValueValidator(2050)   # Максимальный год с запасом
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
        """Строковое представление объекта произведения."""
        return f'{self.name} ({self.year})'


class GenreTitle(models.Model):
    """Промежуточная модель для связи многие-ко-многим между Title и Genre."""
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
        """Строковое представление связи жанр-произведение."""
        return f'{self.title} - {self.genre}'
