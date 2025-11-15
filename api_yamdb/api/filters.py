from django_filters import rest_framework

from reviews.models import Title


class TitleFilter(rest_framework.FilterSet):
    """
    FilterSet для произведений (Title).

    Поддерживает фильтрацию по:
    - name (поиск по частичному совпадению)
    - category (по slug категории)
    - genre (по slug жанра)
    - year (точное совпадение)
    """

    name = rest_framework.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Фильтр по названию произведения (регистронезависимый)'
    )

    category = rest_framework.CharFilter(
        field_name='category__slug',
        help_text='Фильтр по slug категории'
    )

    genre = rest_framework.CharFilter(
        field_name='genre__slug',
        help_text='Фильтр по slug жанра'
    )

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']
