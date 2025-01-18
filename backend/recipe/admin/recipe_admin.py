from django import forms
from django.contrib import admin
from django.utils.html import format_html

from recipe.admin.mixins import (
    DisplayImageMixin, ImagePreviewMixin, RecipesAdminMixin)
from recipe.constants import ITEMS_PER_PAGE
from recipe.models import Recipe, RecipeComponent
from recipe.validators import validate_image_size


class BaseAdmin(admin.ModelAdmin):
    list_per_page = ITEMS_PER_PAGE


class RecipeAdminForm(ImagePreviewMixin, forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_image_preview('image', self.instance)

    def clean_image(self):
        image = self.cleaned_data.get('image')
        validate_image_size(image)
        return image


class RecipeAdmin(DisplayImageMixin, BaseAdmin):
    form = RecipeAdminForm
    fields = (
        'name', 'get_favorites_count', 'author', 'tags', 'cooking_time',
        'text', 'image'
    )
    list_display = (
        'name', 'display_image', 'tag_list', 'author', 'cooking_time', 'text',
        'ingredient_list', 'get_favorites_count'
    )
    readonly_fields = ('get_favorites_count',)
    list_filter = ('tags', 'author')
    search_fields = ('author__username', 'name', 'text', 'tags__name')
    filter_horizontal = ('tags', 'ingredients')
    ordering = ('name',)

    def tag_list(self, recipe):
        return format_html(
            '<br> '.join(
                [
                    f'<a href="/admin/recipe/tag/{tag.id}/">#{tag.name}</a>'
                    for tag in recipe.tags.all()
                ]))

    def ingredient_list(self, recipe):
        ingredients = recipe.components.all()
        return format_html('<br> '.join(
            f'{ingredient.ingredient.name} - {ingredient.quantity}'
            f'{ingredient.ingredient.measurement_unit}'
            for ingredient in ingredients
        ))

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not obj:
            return [
                field for field in fields if field != 'get_favorites_count'
            ]
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('author').prefetch_related(
            'tags', 'components__ingredient'
        )

    def get_favorites_count(self, recipe):
        return recipe.favorites.count()

    get_favorites_count.short_description = 'Понравилось пользователям'
    tag_list.short_description = 'Теги'
    ingredient_list.short_description = 'Ингредиенты'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeComponent
    extra = 1
    fields = ('ingredient', 'quantity', 'measurement_unit')
    readonly_fields = ('measurement_unit',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('ingredient', 'recipe')

    def measurement_unit(self, ingredient):
        return ingredient.ingredient.measurement_unit

    measurement_unit.short_description = 'Единица измерения'


class TagAdmin(RecipesAdminMixin, BaseAdmin):
    list_display = ('name', 'slug', *RecipesAdminMixin.list_display)
    search_fields = ('name', 'slug')


class IngredientAdmin(RecipesAdminMixin, BaseAdmin):
    list_display = (
        'name', 'measurement_unit',
        *RecipesAdminMixin.list_display
    )
    search_fields = ('name',)
