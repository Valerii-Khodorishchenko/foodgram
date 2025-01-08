import csv
import json
from django.core.management.base import BaseCommand
from recipe.models import Ingredient


class Command(BaseCommand):
    help = 'Загружаю ингридиенты в БД из CSV и JSON файлов'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']
        if file_path.endswith('.csv'):
            self.load_from_csv(file_path)
        elif file_path.endswith('.json'):
            self.load_from_json(file_path)
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Неподдерживаемый формат файла. Только .csv и .json'
                )
            )

    def load_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )
        self.stdout.write(self.style.SUCCESS('Ингридиенты загружены из CSV'))

    def load_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                Ingredient.objects.get_or_create(
                    name=item['name'],
                    measurement_unit=item['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Ингридиенты загружены из JSON'))
