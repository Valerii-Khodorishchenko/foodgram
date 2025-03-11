
from djoser.serializers import (
    UserSerializer as DjoserUserSerializer,
    UserCreateSerializer as DjoserUserCreateSerializer
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers


from recipe.models import (
    Follow,
    Ingredient,
    Recipe,
    RecipeComponent,
    Tag,
    User
)
from recipe.validators import (
    validate_favorite_or_cart,
    validate_image,
    validate_ingredients,
    validate_required_fields,
    validate_subscribe,
    validate_tags,
)


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        fields = (
            *UserCreateSerializer.Meta.fields[:-1], 'is_subscribed', 'avatar')
        read_only_fields = ('is_subscribed', 'avatar')

    def get_is_subscribed(self, target_user):
        if (
            (request := self.context.get('request'))
            and request.user.is_authenticated
        ):
            return Follow.objects.filter(
                user=request.user, following=target_user).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(
        required=True,
        error_messages={
            'required': 'Обязательное поле.',
        }
    )

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


class SubscribeSerializer(UserSerializer):
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields[:-1], 'recipes_count', 'recipes',
            UserSerializer.Meta.fields[-1]
        )
        read_only_fields = UserSerializer.Meta.fields

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit', None)
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        return RecipeCartFavoriteSerializer(recipes, many=True).data

    def validate(self, data):
        return validate_subscribe(
            data, self.context['request'].user,
            self.context['target_user'], self.context['request'].method
        )

    def save(self, **kwargs):
        user = self.context['request'].user
        target_user = self.context['target_user']
        method = self.context['request'].method
        if method == 'POST':
            Follow.objects.create(user=user, following=target_user)
        elif method == 'DELETE':
            Follow.objects.filter(user=user, following=target_user).delete()
        return target_user


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields: tuple[str, ...] = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(IngredientSerializer):
    amount = serializers.SerializerMethodField()

    class Meta(IngredientSerializer.Meta):
        fields = (*IngredientSerializer.Meta.fields, 'amount')

    def get_amount(self, obj):
        return obj.components.first().amount


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeCartFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, attrs):
        return validate_favorite_or_cart(
            self.context, self.context.get('category')
        )

    def save(self, **kwargs):
        user = self.context['request'].user
        recipe = self.context['recipe']
        if self.context.get('category', None) == 'favorite':
            return self._process_action(user.favorites, recipe)
        return self._process_action(user.cart, recipe)

    def _process_action(self, related_manager, recipe):
        if self.context['request'].method == 'POST':
            related_manager.add(recipe)
        else:
            related_manager.remove(recipe)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        if (
            (request := self.context.get('request'))
            and request.user.is_authenticated
        ):
            return obj.favorites.filter(id=request.user.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if (
            (request := self.context.get('request'))
            and request.user.is_authenticated
        ):
            return obj.cart.filter(id=request.user.id).exists()
        return False


class RecipeWriteIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeComponent
        fields = ('id', 'amount')


class RecipeCreatePatchSerializer(serializers.ModelSerializer):
    ingredients = RecipeWriteIngredientSerializer(
        source='products',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(
        required=True,
        error_messages={
            'required': 'Обязательное поле.',
        }
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        validate_required_fields(
            data, ('products', 'tags', 'name', 'text', 'cooking_time')
        )
        return data

    def validate_image(self, image):
        return validate_image(image)

    def validate_ingredients(self, ingredients):
        return validate_ingredients(ingredients)

    def validate_tags(self, tags):
        return validate_tags(tags)

    def _handle_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            RecipeComponent.objects.create(
                recipe=recipe,
                product=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('products')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self._handle_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('products')
        tags_data = validated_data.pop('tags')
        image = validated_data.pop('image', None)
        if image is not None and image != instance.image:
            instance.image.delete(save=False)
            instance.image = image
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags_data is not None:
            instance.tags.set(tags_data)
        if ingredients_data is not None:
            instance.components.all().delete()
            self._handle_ingredients(instance, ingredients_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request'),
        }).data
