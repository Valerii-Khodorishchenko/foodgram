import base64

from django.urls import reverse
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from hashids import Hashids
from rest_framework import serializers

from recipe.constants import MAX_PASSWORD_LENGTH
from recipe.models import Ingredient, Recipe, RecipeComponent, Tag, User
from recipe.validators import (
    validate_current_password,
    validate_favorite_or_cart,
    validate_image_size,
    validate_ingredients,
    validate_new_password,
    validate_required_fields,
    validate_subscribe,
    validate_tags,
    validate_user_credentials
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name='temp.' + ext
            )
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields: tuple[str, ...] = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        if (
            (request := self.context.get('request'))
            and request.user.is_authenticated
        ):
            return obj.followings.filter(id=request.user.id).exists()
        return False


class SubscribeSerializer(UserSerializer):
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields[:-1]
        fields += 'recipes_count', 'recipes', UserSerializer.Meta.fields[-1]
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
            user.followings.add(target_user)
        elif method == 'DELETE':
            user.followings.remove(target_user)
        return target_user


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=MAX_PASSWORD_LENGTH, write_only=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        return validate_user_credentials(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(
        required=True,
        error_messages={
            "invalid": "Файл не является корректным изображением.",
            "required": "Обязательное поле.",
            "empty": "Вы отправили пустой файл.",
        },
    )

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, avatar):
        return validate_image_size(avatar)


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )
    current_password = serializers.CharField(required=True)

    def validate_current_password(self, current_password):
        return validate_current_password(
            self.context.get('user'), current_password)

    def validate(self, passwords):
        return validate_new_password(passwords)


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
        source='components',
        many=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        validate_required_fields(data, ['components', 'tags'])
        return data

    def validate_image(self, image):
        return validate_image_size(image)

    def validate_ingredients(self, ingredients):
        return validate_ingredients(ingredients)

    def validate_tags(self, tags):
        return validate_tags(tags)

    def _handle_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            RecipeComponent.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('components')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self._handle_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        validated_data.pop('author', None)
        ingredients_data = validated_data.pop('components', None)
        tags_data = validated_data.pop('tags', None)
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
