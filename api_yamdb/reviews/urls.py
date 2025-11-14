from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet

# Маршрутизатор для API версии 1
api_v1_router = DefaultRouter()

# Эндпоинт для работы с отзывами произведений
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

# Эндпоинт для работы с комментариями к отзывам
api_v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

# Подключение API v1 endpoints
urlpatterns = [
    path('api/v1/', include(api_v1_router.urls)),
]
