from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from recipe.constants import (
    DESCRIPTION_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    INGR_NAME_MAX_LENGTH,
    INGR_MUNIT_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
    SECOND_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH,

)
from recipe.validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        'Псевдоним', max_length=USERNAME_MAX_LENGTH, unique=True, blank=False,
        null=False, validators=[validate_username]
    )
    email = models.EmailField(
        'Адрес электронной почты', unique=True, blank=False, null=False,
        help_text='Поле обязательное для заполнения'
    )
    first_name = models.CharField(
        'Имя', max_length=FIRST_NAME_MAX_LENGTH, blank=False, null=False,
        help_text='Поле обязательное для заполнения'
    )
    last_name = models.CharField(
        'Фамилия', max_length=SECOND_NAME_MAX_LENGTH, blank=False, null=False,
        help_text='Поле обязательное для заполнения'
    )
    avatar = models.ImageField(
        'Фотография профиля', upload_to='avatars/', null=True, default=None
    )
    followings = models.ManyToManyField(
        'self', verbose_name='Подписки', related_name='followers',
        symmetrical=False
    )
    favorites = models.ManyToManyField(
        'Recipe', verbose_name='Избранные рецепты', related_name='favorites'
    )
    cart = models.ManyToManyField(
        'Recipe', verbose_name='Корзина', related_name='cart'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:DESCRIPTION_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента', max_length=INGR_NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=INGR_MUNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH]


class Tag(models.Model):
    name = models.CharField('Название тега', max_length=TAG_NAME_MAX_LENGTH)
    slug = models.SlugField('Идентификатор', max_length=TAG_SLUG_MAX_LENGTH)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиенты', related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Теги', related_name='recipes'
    )
    image = models.ImageField('Изображение блюда', upload_to='dishes/')
    name = models.CharField(
        'Название рецепта',
        max_length=RECIPE_NAME_MAX_LENGTH
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text="Время приготовления в секундах",
        validators=[MinValueValidator(1)]
    )
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE,
        related_name='recipes'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH]


class RecipeComponent(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField('Количество ингредиента')

    class Meta:
        verbose_name = 'Компонент блюда'
        verbose_name_plural = 'Компоненты блюд'
        ordering = ('recipe',)

    def __str__(self):
        return f"{self.ingredient.name[:DESCRIPTION_LENGTH]} ({self.quantity})"
