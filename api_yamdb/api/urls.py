from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GetTokenView, SignUpView, UsersMeView, UserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include('djoser.urls.jwt')),
    path('v1/auth/token/', GetTokenView.as_view(),
         name='create_token'),
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/users/me/', UsersMeView.as_view(), name='users-me'),
    path('v1/', include(router_v1.urls)),
]
