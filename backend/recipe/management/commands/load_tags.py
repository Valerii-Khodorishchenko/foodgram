import csv
import json

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from recipe.models import Tag


class Command(BaseCommand):
    help = 'Загружает теги в БД из CSV или JSON файла'

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

    def create(self, data):
        for tag in data:
            tag_name = tag['name']
            tag_slug = tag['slug']
            if not tag_slug:
                tag_slug = slugify(tag_name)
            if not Tag.objects.filter(name=tag_name).exists():
                Tag.objects.create(name=tag_name, slug=tag_slug)
                self.stdout.write(
                    self.style.SUCCESS(f'Тег "{tag_name}" успешно добавлен.'))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Тег с именем "{tag_name}" уже существует.'
                    ))

    def load_from_csv(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.create(reader)
        self.stdout.write(self.style.SUCCESS('Теги загружены из CSV'))

    def load_from_json(self, file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            data = json.load(file)
            self.create(data)
        self.stdout.write(self.style.SUCCESS('Теги загружены из JSON'))
