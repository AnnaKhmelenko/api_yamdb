from rest_framework import serializers

from reviews.models import Category, Genre, GenreTitle, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений."""
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения названий произведений."""
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'category', 'genre')


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи названий произведений."""
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
        """Создание объекта Title и связей через промежуточную модель."""
        genres_data = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)

        # Создаем связи через промежуточную модель GenreTitle
        for genre in genres_data:
            GenreTitle.objects.create(title=title, genre=genre)

        return title
