from djoser.serializers import UserSerializer as DjoserUserSerializer

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipe.constants import MIN_INGREDIENT_AMOUNT
from recipe.models import (
    Cart,
    Favorites,
    Follow,
    Ingredient,
    Recipe,
    RecipeComponent,
    Tag,
    User
)
from api.validators import (
    validate_image,
    validate_products,
    validate_tags,
)


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = (*DjoserUserSerializer.Meta.fields, 'is_subscribed', 'avatar')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Follow.objects.filter(
                user=request.user, following=author
            ).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, avatar):
        return validate_image(avatar)

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)
        if instance.avatar:
            instance.avatar.delete(save=False)
        instance.avatar = avatar
        instance.save()
        return instance


class SubscriptionReaderSerializer(UserSerializer):
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = read_only_fields = (
            *UserSerializer.Meta.fields, 'recipes_count', 'recipes'
        )

    def get_recipes(self, obj):
        return ReadShortRecipeSerializer(
            obj.recipes.all()[
                :int(self.context.get('request').GET.get(
                    'recipes_limit', 10**10
                ))
            ], many=True).data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        recipe_id = self.context.get('recipe_id')
        recipe_component = RecipeComponent.objects.get(
            recipe_id=recipe_id, product=obj)
        return recipe_component.amount


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ReadShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = read_only_fields = ('id', 'name', 'image', 'cooking_time')


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = read_only_fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def is_exists(self, recipe, model):
        if (
            (request := self.context.get('request'))
            and request.user.is_authenticated
        ):
            return model.objects.filter(
                user=request.user, recipe=recipe).exists()
        return False

    def get_is_favorited(self, recipe):
        return self.is_exists(recipe, Favorites)

    def get_is_in_shopping_cart(self, recipe):
        return self.is_exists(recipe, Cart)

    def get_ingredients(self, obj):
        components = obj.components.all()
        ingredients = [component.product for component in components]
        return RecipeIngredientSerializer(
            ingredients, many=True, context={'recipe_id': obj.id}
        ).data


class WriteRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)

    class Meta:
        model = RecipeComponent
        fields = ('id', 'amount')


class RecipeCreatePatchSerializer(serializers.ModelSerializer):
    ingredients = WriteRecipeIngredientSerializer(
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(
    )

    class Meta:
        model = Recipe
        exclude = ('author',)

    def validate_image(self, image):
        return validate_image(image)

    def validate_ingredients(self, ingredients):
        return validate_products(ingredients)

    def validate_tags(self, tags):
        return validate_tags(tags)

    def _handle_ingredients(self, recipe, ingredients_data):
        recipe.components.all().delete()
        RecipeComponent.objects.bulk_create(
            RecipeComponent(
                recipe=recipe,
                product=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = super().create(validated_data)
        recipe.tags.set(tags_data)
        self._handle_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        self._handle_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance, context=self.context).data
