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
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.')
        if not re.match(USERPATTERN, value):
            raise serializers.ValidationError(
                'Недопустимые символы в username.')
        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if User.objects.filter(username=username).exclude(email=email).exists():
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует.")

        if User.objects.filter(email=email).exclude(username=username).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует.")

        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']

        try:
            user = User.objects.get(username=username, email=email)
            send_confirmation_email(user)
            return user
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=email,
            )
            send_confirmation_email(user)
            return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.')
        if not re.match(USERPATTERN, value):
            raise serializers.ValidationError(
                'Недопустимые символы в username.')
        return value

    def validate_email(self, value):
        if len(value) > 254:
            raise serializers.ValidationError(
                'Длина email не должна превышать 254 символов.')
        return value

    def validate_first_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина first_name не должна превышать 150 символов.')
        return value

    def validate_last_name(self, value):
        if len(value) > 150:
            raise serializers.ValidationError(
                'Длина last_name не должна превышать 150 символов.')
        return value

    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'first_name', 
            'last_name', 'bio', 'role'
        )


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
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'category', 'genre', 'rating')


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
        fields = ('name', 'year', 'description', 'category', 'genre')

    def to_representation(self, instance):
        return TitleReadSerializer(instance, context=self.context).data

    def create(self, validated_data):
        genres_data = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)

        for genre in genres_data:
            GenreTitle.objects.create(title=title, genre=genre)

        return title

    def update(self, instance, validated_data):
        genres_data = validated_data.pop('genre', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if genres_data is not None:
            GenreTitle.objects.filter(title=instance).delete()
            for genre in genres_data:
                GenreTitle.objects.create(title=instance, genre=genre)

        return instance
