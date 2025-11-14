import re
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import serializers

from reviews.models import Category, Genre, GenreTitle, Title

User = get_user_model()
USER_PATTERN = r'^[\w.@+-]+\Z'


def send_confirmation_email(user):
    """Отправляет email с кодом подтверждения."""

    confirmation_code = str(uuid.uuid4())
    user.confirmation_code = confirmation_code
    user.save()

    subject = 'Код подтверждения'
    message = f'Ваш код подтверждения: {confirmation_code}'
    recipient_list = [user.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

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
        if not re.match(USER_PATTERN, value):
            raise serializers.ValidationError(
                'Недопустимые символы в имени пользователя.'
            )
        return value

    def validate(self, data):
        """Валидация уникальности username и email."""
        username = data.get('username')
        email = data.get('email')

        # Проверяем уникальность username
        if (User.objects.filter(username=username)
                .exclude(email=email).exists()):
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует.'
            )

        # Проверяем уникальность email
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

        # Если пользователь уже существует, обновляем email
        if not created:
            user.email = email
            user.save()

        send_confirmation_email(user)
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT токена."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )

    def _validate_field_length(self, value, field_name, max_length):
        """Универсальный метод валидации длины поля."""
        if len(value) > max_length:
            raise serializers.ValidationError(
                f'Длина поля {field_name} не должна превышать '
                f'{max_length} символов.'
            )
        return value

    def validate_username(self, value):
        """Валидация имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.'
            )
        if not re.match(USER_PATTERN, value):
            raise serializers.ValidationError(
                'Недопустимые символы в имени пользователя.'
            )
        return self._validate_field_length(value, 'username', 150)

    def validate_email(self, value):
        """Валидация email."""
        return self._validate_field_length(value, 'email', 254)

    def validate_first_name(self, value):
        """Валидация имени."""
        return self._validate_field_length(value, 'first_name', 150)

    def validate_last_name(self, value):
        """Валидация фамилии."""
        return self._validate_field_length(value, 'last_name', 150)


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
    rating = serializers.IntegerField(read_only=True)

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
        many=True
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'description', 'category', 'genre')

    def to_representation(self, instance):
        """Возвращает данные в формате TitleReadSerializer."""
        return TitleReadSerializer(instance, context=self.context).data

    def _update_genres(self, title, genres_data):
        """Обновляет жанры произведения."""
        # Удаляем старые связи
        GenreTitle.objects.filter(title=title).delete()

        # Создаём новые связи
        genre_objects = [
            GenreTitle(title=title, genre=genre)
            for genre in genres_data
        ]
        GenreTitle.objects.bulk_create(genre_objects)

    def create(self, validated_data):
        """Создание произведения с жанрами."""
        genres_data = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)

        self._update_genres(title, genres_data)
        return title

    def update(self, instance, validated_data):
        """Обновление произведения с жанрами."""
        genres_data = validated_data.pop('genre', None)

        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем жанры если переданы
        if genres_data is not None:
            self._update_genres(instance, genres_data)

        return instance
