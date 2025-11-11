from rest_framework import serializers
from .models import Review


def validate_unique_review(user, title_id):
    """
    Проверяет что пользователь еще не оставлял отзыв на это произведение.
    Вызывается из сериализатора при создании отзыва.
    """
    if Review.objects.filter(author=user, title_id=title_id).exists():
        raise serializers.ValidationError(
            "Вы уже оставляли отзыв на это произведение. "
            "Можно оставить только один отзыв."
        )
