from django.contrib import admin


from recipe.admin.user_admin import UserAdmin
from recipe.admin.recipe_admin import (
    IngredientAdmin,
    RecipeAdmin,
    RecipeIngredientInline,
    TagAdmin
)
from recipe.models import Ingredient, Recipe, Tag, User


RecipeAdmin.inlines = (RecipeIngredientInline,)
admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
