from rest_framework import serializers
from .models import Review, Comment
from .validators import validate_unique_review  # импортируем валидатор


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'score', 'pub_date']

    def validate(self, data):
        """
        Проверяем уникальность отзыва при создании
        """
        # Временно отключаем проверку, пока нет связи с title
        # Когда появится title в модели - раскомментировать:
        # user = self.context['request'].user
        # title_id = data.get('title_id')
        # if title_id and user.is_authenticated:
        #     validate_unique_review(user, title_id)

        return data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'review', 'text', 'pub_date']
