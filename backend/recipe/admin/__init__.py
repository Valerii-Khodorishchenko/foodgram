from django.contrib import admin


from recipe.admin.user_admin import (
    UserAdmin,
    FavoritesCartAdmin,
    FollowAdmin,
)
from recipe.admin.recipe_admin import (
    IngredientAdmin,
    RecipeAdmin,
    RecipeIngredientInline,
    TagAdmin
)
from recipe.models import (
    Cart,
    Favorites,
    Follow,
    Ingredient,
    Recipe,
    Tag,
    User
)


RecipeAdmin.inlines = (RecipeIngredientInline,)
admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Cart, FavoritesCartAdmin)
admin.site.register(Favorites, FavoritesCartAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
