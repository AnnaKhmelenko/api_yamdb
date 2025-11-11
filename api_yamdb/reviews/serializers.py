from rest_framework import serializers
from .models import Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'score', 'pub_date']  # УБРАТЬ title и author
        # read_only_fields = ['author']  # временно закомментировать


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'review', 'text', 'pub_date']  # УБРАТЬ author
        # read_only_fields = ['author']  # временно закомментировать
