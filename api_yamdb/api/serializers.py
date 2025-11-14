import re
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import CustomUser
from api_yamdb.settings import USERPATTERN

User = get_user_model()  # в настройках проекта определена модель CustomUser.


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели CustomUser."""

    def validate_username(self, value):
        """Функция проверки имени пользователя."""
        # проверка длины - 150 символов.
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина username не должна превышать 150 символов.')
        # проверка формата - запрещенные символы.
        if not re.match(USERPATTERN, value):
            raise serializers.ValidationError(
                'У имени пользователя неправильный формат.')
        # имя пользователя не должно начинаться с me.
        if value == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя.')
        return value

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model = CustomUser


class UsersMeSerializer(UserSerializer):
    """Сериализатор для эндпоинта users/me/."""

    role = serializers.CharField(read_only=True)


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=20)

    def validate(self, data):
        """Проверка совпадения кода подтверждения."""
        user = get_object_or_404(User, username=data.get('username'))
        if user.confirmation_code != data.get('confirmation_code'):
            raise serializers.ValidationError(
                'Неправильный код подтверждения!')
        return {'access': str(AccessToken.for_user(user))}


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователей."""

    def validate_username(self, value):
        """Функция проверки имени пользователя."""
        # проверка длины - 150 символов.
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина username не должна превышать 150 символов.')
        # проверка формата - запрещенные символы.
        if not re.match(USERPATTERN, value):
            raise serializers.ValidationError(
                'У имени пользователя неправильный формат.')
        # имя пользователя не должно начинаться с me.
        if value == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя.')
        return value

    class Meta:
        fields = ('username', 'email')
        model = CustomUser
