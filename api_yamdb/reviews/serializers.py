from rest_framework import serializers
from .models import Review, Comment
from .validators import validate_unique_review


class ReviewSerializer(serializers.ModelSerializer):

    def validate(self, data):
        """Проверяем уникальность отзыва при создании."""
        user = self.context['request'].user
        title = data.get('title')
        if title and user.is_authenticated:
            validate_unique_review(user, title.id)
        return data

    class Meta:
        model = Review
        fields = ['id', 'title', 'author', 'text', 'score', 'pub_date']
        read_only_fields = ['author']


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'review', 'author', 'text', 'pub_date']
        read_only_fields = ['author']
