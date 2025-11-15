from rest_framework import serializers

from .models import Comment, Review


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Проверяет, что пользователь не оставлял более одного отзыва."""
        request = self.context.get('request')

        # Проверяем только для POST-запросов
        if request and request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            user = request.user

            # Проверяем существование отзыва
            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError({
                    'detail': 'Вы уже оставляли отзыв на это произведение'
                })

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
