import django_filters

from recipe.models import Ingredient, Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug',
        method='filter_tags'
    )
    is_favorited = django_filters.ChoiceFilter(
        choices=[(1, 'Yes'), (0, 'No')],
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=[(1, 'Yes'), (0, 'No')],
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_tags(self, recipes_set, name, value):
        response = recipes_set
        if value:
            response = recipes_set.none()
            for tag in value:
                response |= recipes_set.filter(tags__slug=tag.slug)
        return response.distinct()

    def filter_is_favorited(self, recipes_set, name, value):
        if self.request.user.is_authenticated and value == '1':
            user = self.request.user
            recipes_set = recipes_set.filter(favorited_by__user=user)
        return recipes_set

    def filter_is_in_shopping_cart(self, recipes_set, name, value):
        if self.request.user.is_authenticated and value == '1':
            user = self.request.user
            recipes_set = recipes_set.filter(in_carts__user=user)
        return recipes_set


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
