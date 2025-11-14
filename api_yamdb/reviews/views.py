from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .models import Comment, Review, Title
from .serializers import CommentSerializer, ReviewSerializer
from api.permissions import IsModeratorOrAuthor


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
        IsModeratorOrAuthor
    ]

    def get_queryset(self):
        """
        Возвращает queryset отзывов для конкретного произведения.

        Returns:
            QuerySet: Отзывы для произведения с title_id из URL
        """
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id).select_related(
            'author', 'title'
        )

    def perform_create(self, serializer):
        """
        Создает отзыв с автоматическим заполнением автора и произведения.

        Args:
            serializer: Сериализатор с проверенными данными
        """
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)

    def update(self, request, *args, **kwargs):
        """
        Обрабатывает запросы на обновление, запрещая метод PUT.

        Returns:
            Response: 405 ошибка для PUT, либо результат PATCH
        """
        if request.method == 'PUT':
            return Response(
                {'detail': 'Method "PUT" not allowed. Use "PATCH" instead.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с комментариями к отзывам.

    Поддерживает операции:

    - GET /titles/{title_id}/reviews/{review_id}/comments/
    - список комментариев

    - POST /titles/{title_id}/reviews/{review_id}/comments/
    - создать комментарий

    - GET /titles/{title_id}/reviews/{review_id}/comments/{id}/
    - получить комментарий

    - PATCH /titles/{title_id}/reviews/{review_id}/comments/{id}/
    - обновить комментарий

    - DELETE /titles/{title_id}/reviews/{review_id}/comments/{id}/
    - удалить комментарий
    """

    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsModeratorOrAuthor
    ]

    def get_queryset(self):
        """
        Возвращает queryset комментариев для конкретного отзыва.

        Returns:
            QuerySet: Комментарии для отзыва с review_id из URL
        """
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id).select_related(
            'author', 'review'
        )

    def perform_create(self, serializer):
        """
        Создает комментарий с автоматическим заполнением автора и отзыва.

        Args:
            serializer: Сериализатор с проверенными данными
        """
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        """
        Обрабатывает запросы на обновление, запрещая метод PUT.

        Returns:
            Response: 405 ошибка для PUT, либо результат PATCH
        """
        if request.method == 'PUT':
            return Response(
                {'detail': 'Method "PUT" not allowed. Use "PATCH" instead.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)
