from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignUpView, GetTokenView, UserMeView, UsersViewSet, CategoryViewSet, GenreViewSet, TitleViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UsersViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', GetTokenView.as_view(), name='token'),
    path('v1/users/me/', UserMeView.as_view({'get': 'retrieve', 'put': 'update'}), name='user-me'),
    path('v1/', include('djoser.urls.jwt')),
]
