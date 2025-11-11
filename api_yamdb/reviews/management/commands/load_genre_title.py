import csv
import os

from django.core.management.base import BaseCommand

from reviews.models import Genre, GenreTitle, Title


class Command(BaseCommand):
    help = 'Загрузка связей произведений и жанров из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Путь к CSV файлу genre_title.csv'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'Файл {csv_file} не найден!')
            )
            return

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])

                    GenreTitle.objects.get_or_create(
                        title=title,
                        genre=genre
                    )
                except Title.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Произведение с id {row["title_id"]} не найдено')
                    )
                except Genre.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Жанр с id {row["genre_id"]} не найден')
                    )

        self.stdout.write(
            self.style.SUCCESS('Связи жанров и произведений успешно загружены')
        )
