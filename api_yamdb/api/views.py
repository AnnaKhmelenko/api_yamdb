from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from .filters import TitleFilter
from .permissions import (
    IsAdminOnly,
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    SignUpResponseSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    TokenSerializer,
    UserSerializer,
)

User = get_user_model()


class SignUpView(APIView):
    """View для регистрации пользователей."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Обработка POST-запроса для регистрации."""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = SignUpResponseSerializer(user)
        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK
        )


class GetTokenView(APIView):
    """View для получения JWT токена."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Обработка POST-запроса для получения токена."""
        username = request.data.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Пользователь не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(username=username)
        token = str(AccessToken.for_user(user))
        return Response({'token': token})


class UsersViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdminOnly,)
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """Получение и обновление данных текущего пользователя."""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        serializer.save(role=request.user.role)
        return Response(serializer.data)


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


class CategoryViewSet(BaseCategoryGenreViewSet):
    """ViewSet для управления категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseCategoryGenreViewSet):
    """ViewSet для управления жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления произведениями."""

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с отзывами на произведения.
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
