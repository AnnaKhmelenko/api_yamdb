from django.contrib import admin
from .models import Review, Comment


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