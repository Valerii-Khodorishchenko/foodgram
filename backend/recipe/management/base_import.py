import csv
import json

from django.core.management.base import BaseCommand


class BaseImport(BaseCommand):
    help = 'Импорт данных из CSV и JSON файлов'
    unique_fields = ('name',)
    model = None

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            if file_path.endswith('.csv'):
                added_count = self.load_from_csv(file_path)
                print(added_count)
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
        new_objects = [
            self.model(**item) for item in data
            if not (self.unique_fields and self.model.objects.filter(
                **{fld: item[fld] for fld in self.unique_fields if fld in item}
            ).exists())
        ]
        return len(self.model.objects.bulk_create(new_objects))

    def load_from_csv(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return self.create(csv.DictReader(file))

    def load_from_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return self.create(json.load(file))
