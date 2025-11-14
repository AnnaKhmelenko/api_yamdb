from rest_framework import serializers

from .models import Comment, Review


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'pub_date', 'author')

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

    def validate_score(self, value):
        """Проверяет, что оценка находится в допустимом диапазоне."""
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10'
            )
        return value

    def create(self, validated_data):
        """Создает отзыв с автоматическим заполнением автора и произведения."""
        # Добавляем автора из контекста запроса
        validated_data['author'] = self.context['request'].user

        # Добавляем произведение из URL параметров
        view = self.context['view']
        validated_data['title_id'] = view.kwargs.get('title_id')

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Обновляет отзыв, запрещая изменение автора и произведения."""
        # Запрещаем изменение автора и произведения при обновлении
        validated_data.pop('author', None)
        validated_data.pop('title_id', None)

        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'pub_date', 'author')

    def create(self, validated_data):
        """Создает комментарий с автоматическим заполнением автора и отзыва."""
        # Добавляем автора из контекста запроса
        validated_data['author'] = self.context['request'].user

        # Добавляем отзыв из URL параметров
        view = self.context['view']
        validated_data['review_id'] = view.kwargs.get('review_id')

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Обновляет комментарий, запрещая изменение автора и отзыва."""
        # Запрещаем изменение автора и отзыва при обновлении
        validated_data.pop('author', None)
        validated_data.pop('review_id', None)

        return super().update(instance, validated_data)
