from recipe.apps import custom_admin_site

from recipe.admin.user_admin import CustomUserAdmin
from recipe.admin.recipe_admin import (
    IngredientAdmin,
    RecipeAdmin,
    RecipeIngredientInline,
    TagAdmin
)
from recipe.models import Ingredient, Recipe, Tag, User


RecipeAdmin.inlines = (RecipeIngredientInline,)
custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(Recipe, RecipeAdmin)
custom_admin_site.register(Tag, TagAdmin)
custom_admin_site.register(Ingredient, IngredientAdmin)
