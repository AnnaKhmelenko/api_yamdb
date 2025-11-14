from django.contrib import admin
from .models import Category, Genre, Title, GenreTitle, Review, Comment


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
    list_display = ('name', 'year', 'category')
    list_display_links = ('name',)
    list_filter = ('category', 'year')
    search_fields = ('name', 'category__name')


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    """Админ-панель для связи произведений и жанров."""
    list_display = ('title', 'genre')
    list_display_links = ('title',)
    list_filter = ('genre',)
    search_fields = ('title__name', 'genre__name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'score', 'pub_date')
    list_filter = ('pub_date', 'score')
    search_fields = ('text',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'pub_date')
    list_filter = ('pub_date',)
    search_fields = ('text',)
