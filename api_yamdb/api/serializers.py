import re

from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Genre, Title

User = get_user_model()


class SignUpResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для ответа при регистрации."""

    class Meta:
        model = User
        fields = ('username', 'email')


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        """Валидация имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.'
            )

        # Проверка на допустимые символы
        invalid_chars = re.sub(r'[\w.@+-]', '', value)
        if invalid_chars:
            raise serializers.ValidationError(
                f'Недопустимые символы в имени пользователя: {invalid_chars}'
            )
        return value

    def validate(self, data):
        """Валидация уникальности username и email."""
        username = data.get('username')
        email = data.get('email')

        if (User.objects.filter(username=username)
                .exclude(email=email).exists()):
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует.'
            )

        if (User.objects.filter(email=email)
                .exclude(username=username).exists()):
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )

        return data

    def create(self, validated_data):
        """Создание или получение пользователя."""
        username = validated_data['username']
        email = validated_data['email']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        if not created:
            user.email = email
            user.save()

        from api.utils import send_confirmation_email
        send_confirmation_email(user)
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT токена."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        """Валидация кода подтверждения."""
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'username': 'Пользователь не найден'},
                code='user_not_found'
            )

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения'}
            )

        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True, default=None)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description',
            'category', 'genre', 'rating'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        allow_null=False,
        allow_empty=False
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'category', 'genre')

    def to_representation(self, instance):
        """Возвращает данные в формате TitleReadSerializer."""
        return TitleReadSerializer(instance, context=self.context).data
