from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from recipe.admin.filters import CookingTimeFilter
from recipe.admin.mixins import DisplayImageMixin, RecipesAdminMixin
from recipe.constants import ITEMS_PER_PAGE
from recipe.models import RecipeComponent


class BaseAdmin(admin.ModelAdmin):
    list_per_page = ITEMS_PER_PAGE


class RecipeAdmin(DisplayImageMixin, BaseAdmin):
    fields = (
        'name', 'author', 'tags', 'cooking_time',
        'text', 'image'
    )
    list_display = (
        'name', 'display_image', 'tag_list', 'author', 'cooking_time',
        'ingredient_list', 'get_favorites_count'
    )
    list_filter = ('tags', 'author', CookingTimeFilter)
    search_fields = ('author__username', 'name', 'tags__name')
    filter_horizontal = ('tags', 'ingredients')
    ordering = ('name',)

    @admin.display(description='Теги')
    @mark_safe
    def tag_list(self, recipe):
        return ('<br> '.join(
            '<a href="{0}">#{1}</a>'.format(
                reverse('admin:recipe_tag_change', args=[tag.id]),
                tag.name
            )
            for tag in recipe.tags.all()
        ))

    @admin.display(description='Ингредиенты')
    @mark_safe
    def ingredient_list(self, recipe):
        return ('<br> '.join(
            f'{ingredient.ingredient.name} - {ingredient.amount}'
            f'{ingredient.ingredient.measurement_unit}'
            for ingredient in recipe.components.all()
        ))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author').prefetch_related(
            'tags', 'components__ingredient'
        )

    @admin.display(description='Понравилось')
    def get_favorites_count(self, recipe):
        return recipe.favorites.count()

    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     from recipe.admin.mixins import get_img
    #     from recipe.models import Recipe
    #     from recipe.constants import DISPLAY_IMAGE_SIZE
    #     field = super().formfield_for_dbfield(db_field, **kwargs)
    #     instance = kwargs.get('instance')
    #     print(instance)
    #     if db_field.name == 'image':
    #         request  = kwargs.get('request')
    #         object_id = request.resolver_match.kwargs.get('object_id')
    #         if recipe := Recipe.objects.filter(id=object_id).first():
    #             image_url = recipe.image.url
    #             field.help_text = get_img(image_url, DISPLAY_IMAGE_SIZE)
    #     return field


class RecipeIngredientInline(admin.TabularInline):
    # TODO: Вернуться после исправления моделей (убрать лишний класс)
    model = RecipeComponent
    extra = 1
    fields = ('ingredient', 'amount', 'measurement_unit')
    readonly_fields = ('measurement_unit',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('ingredient', 'recipe')

    @admin.display(description='Единица измерения')
    def measurement_unit(self, ingredient):
        return ingredient.ingredient.measurement_unit


class TagAdmin(RecipesAdminMixin, BaseAdmin):
    list_display = ('name', 'slug', *RecipesAdminMixin.list_display)
    search_fields = ('name', 'slug')


class IngredientAdmin(RecipesAdminMixin, BaseAdmin):
    list_display = (
        'name', 'measurement_unit',
        *RecipesAdminMixin.list_display
    )
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
