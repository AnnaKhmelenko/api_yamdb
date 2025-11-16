from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter

from .permissions import IsAdminOrReadOnly


class BaseCategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Базовый ViewSet для категорий и жанров."""

    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
