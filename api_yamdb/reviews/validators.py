from rest_framework import serializers

from .models import Review


def validate_unique_review(author, title_id):
    """Проверяет что пользователь еще не оставлял отзыв на это произведение."""

    if Review.objects.filter(author=author, title_id=title_id).exists():
        raise serializers.ValidationError({
            'detail': 'Вы уже оставляли отзыв на это произведение.',
            'code': 'unique_review_violation'
        })


def validate_score_range(score):
    """
    Проверяет, что оценка находится в допустимом диапазоне.

    Args:
        score: Оценка для проверки (1-10)

    Raises:
        serializers.ValidationError: Если оценка вне диапазона
    """
    if not 1 <= score <= 10:
        raise serializers.ValidationError({
            'score': 'Оценка должна быть в диапазоне от 1 до 10.'
        })
