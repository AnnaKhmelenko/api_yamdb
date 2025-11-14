from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView

from .confirmations import send_confirmation_code
from .permissions import IsAdminUser
from .serializers import (
    GetTokenSerializer,
    SignupSerializer,
    UserSerializer,
    UsersMeSerializer
)

User = get_user_model()  # В настройках определена модель CustomUser


class UserViewSet(viewsets.ModelViewSet):
    """Вью для модели CustomUser."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAuthenticated, IsAdminUser)


class UsersMeView(APIView):
    """Вью для эндпоинта users/me/."""

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Переопределим метод GET."""
        me = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(me)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Переопределим метод PATCH."""
        me = get_object_or_404(User, username=request.user.username)
        serializer = UsersMeSerializer(me, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(TokenObtainPairView):
    """Вью для получения токена"""

    serializer_class = GetTokenSerializer


class SignUpView(APIView):
    """Вью для регистрации пользователей."""

    permission_classes = (AllowAny,)

    def post(self, request):
        """Переопределим метод POST."""
        serializer = SignupSerializer(data=request.data)
        if User.objects.filter(username=request.data.get('username'),
                               email=request.data.get('email')).exists():
            send_confirmation_code(request)
            return Response(request.data, status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_confirmation_code(request)
        return Response(serializer.data, status=status.HTTP_200_OK)
