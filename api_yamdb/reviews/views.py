from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets

from .models import Review, Title
from .serializers import CommentSerializer, ReviewSerializer
from api.permissions import IsAuthorModeratorAdminOrReadOnly


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с отзывами на произведения.

    Поддерживает операции:
    - GET /titles/{title_id}/reviews/ - список отзывов
    - POST /titles/{title_id}/reviews/ - создать отзыв
    - GET /titles/{title_id}/reviews/{id}/ - получить отзыв
    - PATCH /titles/{title_id}/reviews/{id}/ - частично обновить отзыв
    - DELETE /titles/{title_id}/reviews/{id}/ - удалить отзыв
    """

    serializer_class = ReviewSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminOrReadOnly
    ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        """Возвращает произведение по title_id из URL."""
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        """
        Возвращает queryset отзывов для конкретного произведения.
        """
        title = self.get_title()
        return title.reviews.select_related('author')

    def perform_create(self, serializer):
        """
        Создает отзыв с автоматическим заполнением автора и произведения.
        """
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с комментариями к отзывам.

    Поддерживает операции:
    - GET /titles/{title_id}/reviews/{review_id}/comments/
    - POST /titles/{title_id}/reviews/{review_id}/comments/
    - GET /titles/{title_id}/reviews/{review_id}/comments/{id}/
    - PATCH /titles/{title_id}/reviews/{review_id}/comments/{id}/
    - DELETE /titles/{title_id}/reviews/{review_id}/comments/{id}/
    """

    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminOrReadOnly
    ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        """Возвращает отзыв по title_id и review_id из URL."""
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id, title_id=title_id)

    def get_queryset(self):
        """
        Возвращает queryset комментариев для конкретного отзыва.
        """
        review = self.get_review()
        return review.comments.select_related('author')

    def perform_create(self, serializer):
        """
        Создает комментарий с автоматическим заполнением автора и отзыва.
        """
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)
