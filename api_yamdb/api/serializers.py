from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.validators import validate_username
from api.utils import send_confirmation_email
from reviews.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME


User = get_user_model()


class SignUpResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для ответа при регистрации."""

    class Meta:
        model = User
        fields = ('username', 'email')


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(max_length=MAX_LENGTH_EMAIL)
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        validators=[validate_username]
    )

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
            email=email
        )

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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыва."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Проверяет, что пользователь не оставлял более одного отзыва."""
        request = self.context.get('request')

        # Проверяем только для POST-запросов
        if request and request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            user = request.user

            # Проверяем существование отзыва
            if Review.objects.filter(title_id=title_id, author=user).exists():
                raise serializers.ValidationError({
                    'detail': 'Вы уже оставляли отзыв на это произведение'
                })

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
