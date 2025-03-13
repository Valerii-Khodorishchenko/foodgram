from recipe.management.base_import import BaseImport
from recipe.models import Ingredient


class Command(BaseImport):
    halp = 'Импорт ингредиентов из CSV или JSON файла'
    model = Ingredient
