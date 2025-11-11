from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Основные модели
class Review(models.Model):
    # ВРЕМЕННО убираем связи - будут добавлены позже
    # title = models.ForeignKey('titles.Title', ...)
    # author = models.ForeignKey('users.CustomUser', ...)

    text = models.TextField(verbose_name='Текст отзыва')
    score = models.IntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Отзыв {self.id}'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments', 
        verbose_name='Отзыв'
    )
    # author = models.ForeignKey('users.CustomUser', ...)  # временно убираем

    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-pub_date']

    def __str__(self):
        return f'Комментарий {self.id}'
