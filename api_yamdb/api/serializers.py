import re
import uuid
from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from reviews.models import CustomUser, Category, Genre, GenreTitle, Title

User = get_user_model()

USERPATTERN = r'^[\w.@+-]+\Z'


def send_confirmation_email(user):
    confirmation_code = str(uuid.uuid4())
    user.confirmation_code = confirmation_code
    user.save()
    subject = 'Код подтверждения'
    message = f'Ваш код подтверждения: {confirmation_code}'
    recipient_list = [user.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate_username(self, value):
        if not re.match(USERPATTERN, value):
            raise serializers.ValidationError('Недопустимые символы в username.')
        return value

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Пользователь с таким username уже существует.")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        send_confirmation_email(user)
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_username(self, value):
        if len(value) > 150:
            raise serializers.ValidationError('Длина username не должна превышать 150 символов.')
        if not re.match(USERPATTERN, value):
            raise serializers.ValidationError('У имени пользователя неправильный формат.')
        return value

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError('Длина email не должна превышать 254 символов.')
        return value

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
        )
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'category', 'genre')


class TitleWriteSerializer(serializers.ModelSerializer):
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
        fields = ('name', 'year', 'category', 'genre')

    def create(self, validated_data):
        genres_data = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres_data:
            GenreTitle.objects.create(title=title, genre=genre)
        return title
