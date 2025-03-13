from recipe.management.base_import import BaseImport
from recipe.models import Tag


class Command(BaseImport):
    help = 'Загружает теги в БД из CSV или JSON файла'
    model = Tag
