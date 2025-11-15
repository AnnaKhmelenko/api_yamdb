from django.contrib import admin

from .models import Category, Genre, Title, Review, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ-панель для категорий."""
    list_display = ('name', 'slug')
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Админ-панель для жанров."""
    list_display = ('name', 'slug')
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Админ-панель для произведений."""
    list_display = ('name', 'year', 'category', 'display_genres')
    list_display_links = ('name',)
    list_filter = ('category', 'year', 'genre')
    search_fields = ('name', 'category__name', 'genre__name')
    filter_horizontal = ('genre',)

    def display_genres(self, obj):
        """Отображает жанры произведения в админке."""
        return ", ".join([genre.name for genre in obj.genre.all()])
    display_genres.short_description = 'Жанры'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админ-панель для отзывов."""
    list_display = ('title', 'author', 'score', 'pub_date')
    list_display_links = ('title',)
    list_filter = ('pub_date', 'score')
    search_fields = ('title__name', 'author__username', 'text')
    readonly_fields = ('pub_date',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админ-панель для комментариев."""
    list_display = ('review', 'author', 'pub_date')
    list_display_links = ('review',)
    list_filter = ('pub_date',)
    search_fields = ('review__text', 'author__username', 'text')
    readonly_fields = ('pub_date',)
