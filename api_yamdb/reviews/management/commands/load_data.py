import csv
from django.core.management.base import BaseCommand
from django.db import transaction

from reviews.models import Category, Genre, Title, GenreTitle, Review, Comment
from users.models import User


class Command(BaseCommand):
    help = 'Загрузка всех данных из CSV файлов'

    def handle(self, *args, **options):
        # Порядок важен из-за внешних ключей
        load_functions = [
            self.load_users,
            self.load_category,
            self.load_genre,
            self.load_titles,
            self.load_genre_title,
            self.load_reviews,
            self.load_comments
        ]

        with transaction.atomic():
            for load_func in load_functions:
                try:
                    load_func()
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Ошибка в {load_func.__name__}: {e}')
                    )
                    raise

        self.stdout.write(
            self.style.SUCCESS('Все данные успешно загружены')
        )

    def load_users(self):
        """Загрузка пользователей"""
        csv_file = 'static/data/users.csv'
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                User.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'role': row['role'],
                        'bio': row['bio'],
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                    }
                )
        self.stdout.write('Пользователи загружены')

    def load_category(self):
        """Загрузка категорий"""
        csv_file = 'static/data/category.csv'
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Category.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug']
                    }
                )
        self.stdout.write('Категории загружены')

    def load_genre(self):
        """Загрузка жанров"""
        csv_file = 'static/data/genre.csv'
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                Genre.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug']
                    }
                )
        self.stdout.write('Жанры загружены')

    def load_titles(self):
        """Загрузка произведений"""
        csv_file = 'static/data/titles.csv'
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = Category.objects.get(id=row['category'])
                Title.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'year': row['year'],
                        'category': category,
                    }
                )
        self.stdout.write('Произведения загружены')

    def load_genre_title(self):
        """Загрузка связей жанров и произведений"""
        csv_file = 'static/data/genre_title.csv'
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
                GenreTitle.objects.get_or_create(
                    title=title,
                    genre=genre
                )
        self.stdout.write('Связи жанров загружены')

    def load_reviews(self):
        """Загрузка отзывов"""
        csv_file = 'static/data/review.csv'
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = Title.objects.get(id=row['title_id'])
                author = User.objects.get(id=row['author'])
                Review.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'title': title,
                        'text': row['text'],
                        'author': author,
                        'score': row['score'],
                        'pub_date': row['pub_date'],
                    }
                )
        self.stdout.write('Отзывы загружены')

    def load_comments(self):
        """Загрузка комментариев"""
        csv_file = 'static/data/comments.csv'
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                review = Review.objects.get(id=row['review_id'])
                author = User.objects.get(id=row['author'])
                Comment.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'review': review,
                        'text': row['text'],
                        'author': author,
                        'pub_date': row['pub_date'],
                    }
                )
        self.stdout.write('Комментарии загружены')
