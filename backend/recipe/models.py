from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from recipe.constants import (
    DESCRIPTION_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    INGREDIENT_NAME_MAX_LENGTH,
    INGREDIENT_MUNIT_MAX_LENGTH,
    MIN_INGREDIENT_AMOUNT,
    RECIPE_NAME_MAX_LENGTH,
    SECOND_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
    TIME_MIN_VALUE,
    USERNAME_MAX_LENGTH,
)
from recipe.validators import validate_username


class User(AbstractUser):
    username = models.CharField(
        'Псевдоним', max_length=USERNAME_MAX_LENGTH, unique=True,
        validators=[validate_username],
    )
    email = models.EmailField(
        'Адрес электронной почты', unique=True,
        help_text='Адрес электронной почты. Должен быть уникальным.'
    )
    first_name = models.CharField(
        'Имя', max_length=FIRST_NAME_MAX_LENGTH,
        help_text='Введите имя.'
    )
    last_name = models.CharField(
        'Фамилия', max_length=SECOND_NAME_MAX_LENGTH,
        help_text='Введите фамилию.'
    )
    avatar = models.ImageField(
        'Фотография профиля', upload_to='avatars/',
        help_text='Загрузите изображение для аватарки.',
        null=True, default=None,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:DESCRIPTION_LENGTH]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        related_name='authors',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('following',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_user_following'
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.following}'


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=INGREDIENT_NAME_MAX_LENGTH,
        help_text='Название продукта.'
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=INGREDIENT_MUNIT_MAX_LENGTH,
        help_text='Единица измерения продукта.'
    )

    class Meta:
        default_related_name = 'ingredients'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH]


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=TAG_NAME_MAX_LENGTH, unique=True,
        help_text='Уникальное название тега.'
    )
    slug = models.SlugField(
        'Идентификатор', max_length=TAG_SLUG_MAX_LENGTH, unique=True,
        help_text='Уникальный slug тега, состоящий из латинских букв, цифр и'
                  ' подчеркиваний.'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeComponent', verbose_name='продукты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    image = models.ImageField(
        'Изображение блюда', upload_to='food image',
        help_text='Загрузите изображение рецепта.',
    )
    name = models.CharField(
        'Название',
        max_length=RECIPE_NAME_MAX_LENGTH,
        help_text='Название рецепта.'
    )
    text = models.TextField('Описание', help_text='Описание рецепта.')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(TIME_MIN_VALUE)],
        help_text='Время приготовления в минутах.'
    )
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE,
        help_text='Пользователь добавивший рецепт'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации',
        help_text='Дата и время создания рецепта'
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH]


class RecipeComponent(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    product = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Продукт')
    amount = models.PositiveSmallIntegerField(
        'Мера',
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)],
        help_text='Единица измерений продукта'
    )

    class Meta:
        default_related_name = 'components'
        verbose_name = 'Компонент блюда'
        verbose_name_plural = 'Компоненты блюд'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'product'),
                name='ingredient_in_recipe'
            ),
        )

    def __str__(self):
        return f'{self.product.name[:DESCRIPTION_LENGTH]} ({self.amount})'


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class Favorites(UserRecipeRelation):
    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )
        unique_together = ('user', 'recipe')


class Cart(UserRecipeRelation):
    class Meta:
        default_related_name = 'carts'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
