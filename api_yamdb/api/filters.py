import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """
    FilterSet для произведений (Title).

    Поддерживает фильтрацию по:
    - name (поиск по частичному совпадению)
    - category (по slug категории)
    - genre (по slug жанра)
    - year (точное совпадение)
    """

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        help_text='Фильтр по названию произведения (регистронезависимый)'
    )

    category = django_filters.CharFilter(
        field_name='category__slug',
        help_text='Фильтр по slug категории'
    )

    genre = django_filters.CharFilter(
        field_name='genre__slug',  # ← ОПТИМИЗАЦИЯ: используем прямое M2M поле
        help_text='Фильтр по slug жанра'
    )

    year = django_filters.NumberFilter(
        field_name='year',
        help_text='Фильтр по году выпуска'
    )

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']
