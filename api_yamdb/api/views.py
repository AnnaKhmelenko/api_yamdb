from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from reviews.models import CustomUser
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer, UserCreateSerializer
from .permissions import IsAdminOrReadOnly, IsModeratorOrAuthor, IsAuthorOrReadOnly

from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = UserCreateSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTokenView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        code = serializer.validated_data['confirmation_code']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=400)
        if user.confirmation_code != code:
            return Response({'error': 'Неверный код подтверждения'}, status=400)
        token = str(AccessToken.for_user(user))
        return Response({'token': token})


class UserMeView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAuthorOrReadOnly)

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.save()


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )
