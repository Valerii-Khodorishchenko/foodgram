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

    def filter_tags(self, queryset, name, value):
        slugs = [tag.slug for tag in value]
        return queryset.filter(tags__slug__in=slugs).distinct()

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value == '1':
            user = self.request.user
            queryset = queryset.filter(favorites=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value == '1':
            user = self.request.user
            queryset = queryset.filter(cart=user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
