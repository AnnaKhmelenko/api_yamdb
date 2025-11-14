import csv
import os

from django.core.management.base import BaseCommand

from reviews.models import Category, Title


class Command(BaseCommand):
    help = 'Загрузка произведений из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_file',
                            type=str,
                            help='Путь к CSV файлу titles.csv'
                            )

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        # Проверка что файл существует
        if not os.path.exists(csv_file):
            self.stdout.write(
                self.style.ERROR(f'Файл {csv_file} не найден!')
            )
            return

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # Получаем категорию
                try:
                    category = Category.objects.get(id=row['category'])
                except Category.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Категория с id {row["category"]} не найдена')
                    )
                    continue

                # Создаем или обновляем произведение (БЕЗ description)
                title, created = Title.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'year': row['year'],
                        'category': category,
                        # УБРАТЬ 'description' - этого поля нет в модели
                    }
                )

        self.stdout.write(
            self.style.SUCCESS('Произведения успешно загружены')
        )
