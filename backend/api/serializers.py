from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers


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
    validate_required_fields,
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
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        return RecipeCartFavoriteSerializer(recipes, many=True).data


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

    def validate_ingredients(self, products):
        return validate_products(products)

    def validate_tags(self, tags):
        return validate_tags(tags)

    def _handle_products(self, recipe, products_data):
        for product_data in products_data:
            RecipeComponent.objects.create(
                recipe=recipe,
                product=product_data['id'],
                amount=product_data['amount']
            )

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self._handle_products(recipe, products_data)
        return recipe

    def update(self, instance, validated_data):
        products_data = validated_data.pop('products')
        tags_data = validated_data.pop('tags')
        image = validated_data.pop('image', None)
        if image is not None and image != instance.image:
            instance.image.delete(save=False)
            instance.image = image
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags_data is not None:
            instance.tags.set(tags_data)
        if products_data is not None:
            instance.components.all().delete()
            self._handle_products(instance, products_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request'),
        }).data
