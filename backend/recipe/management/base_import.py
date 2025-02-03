import csv
import json

from django.core.management.base import BaseCommand


class BaseImport(BaseCommand):
    help = 'Импорт данных из CSV и JSON файлов'
    unique_fields = None

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']
        if file_path.endswith('.csv'):
            self.load_from_csv(file_path)
        elif file_path.endswith('.json'):
            self.load_from_json(file_path)
        else:
            self.stdout.write(self.style.ERROR(
                'Неподдерживаемый формат файла. Только .csv и .json'
            ))

    def create(self, data):
        queryset = self.model.objects.all()
        list_objects_create = []
        for item in data:
            if self.unique_fields is not None:
                filter_unique_fields = {
                    field: item[field]
                    for field in self.unique_fields
                    if field in item
                }
            if (
                (obj := queryset.filter(**filter_unique_fields))
                and obj.exists()
            ):
                self.stdout.write(self.style.WARNING(
                    f'Запись "{obj.first()}" уже существует.'
                ))
            else:
                obj = self.model(**item)
                list_objects_create.append(obj)
                self.stdout.write(self.style.SUCCESS(
                    f'Запись "{obj}" успешно добавлена.'
                ))
        self.model.objects.bulk_create(list_objects_create)

    def load_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.create(reader)
        self.stdout.write(self.style.SUCCESS('Данные загружены из CSV'))

    def load_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.create(data)
        self.stdout.write(self.style.SUCCESS('Данные загружены из JSON'))
