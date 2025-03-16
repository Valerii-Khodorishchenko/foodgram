import csv
import json

from django.core.management.base import BaseCommand


class BaseImport(BaseCommand):
    help = 'Импорт данных из CSV и JSON файлов'
    model = None

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            if file_path.endswith('.csv'):
                added_count = self.load_from_csv(file_path)
            elif file_path.endswith('.json'):
                added_count = self.load_from_json(file_path)
            else:
                self.stdout.write(
                    self.style.ERROR(
                        'Неподдерживаемый формат файла. Только .csv и .json'
                    ))
                return

            self.stdout.write(self.style.SUCCESS(
                f'Добавлено {added_count}/{self.model.objects.count()}'
                f' записей из {file_path}'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка импорта: {e}'))

    def create(self, data):
        return len(self.model.objects.bulk_create(
            [self.model(**item) for item in data],
            ignore_conflicts=True
        ))

    def load_from_file(self, file_path, file_type):
        with open(file_path, 'r', encoding='utf-8') as file:
            if file_type == 'csv':
                return csv.DictReader(file)
            elif file_type == 'json':
                return json.load(file)

    def load_from_csv(self, file_path):
        return self.create(self.load_from_file(file_path, 'csv'))

    def load_from_json(self, file_path):
        return self.create(self.load_from_file(file_path, 'json'))
