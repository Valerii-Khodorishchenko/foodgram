from recipe.models import Ingredient
from recipe.management.base_import import BaseImport


class Command(BaseImport):
    halp = 'Импорт ингредиентов из CSV или JSON файла'
    model = Ingredient
    unique_fields = ('name', 'measurement_unit')
