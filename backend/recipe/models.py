from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipe.constants import (
    DESCRIPTION_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    INGR_NAME_MAX_LENGTH,
    INGR_MUNIT_MAX_LENGTH,
    MAX_SIZE_IMG,
    MAX_URL_SIZE,
    RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
    SECOND_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
)
from recipe.validators import validate_image_size, validate_username


class User(AbstractUser):
    username = models.CharField(
        'Псевдоним', max_length=USERNAME_MAX_LENGTH, unique=True, blank=False,
        null=False, validators=[validate_username],
        help_text='Уникальный псевдоним. Используйте только буквы, цифры'
        ' и символы @/./+/-/_.'
    )
    email = models.EmailField(
        'Адрес электронной почты', unique=True, blank=False, null=False,
        help_text='Адрес электронной почты. Должен быть уникальным.'
    )
    first_name = models.CharField(
        'Имя', max_length=FIRST_NAME_MAX_LENGTH, blank=False, null=False,
        help_text=f'Введите имя. Не более {FIRST_NAME_MAX_LENGTH} символов.'
    )
    last_name = models.CharField(
        'Фамилия', max_length=SECOND_NAME_MAX_LENGTH, blank=False, null=False,
        help_text='Введите фамилию. Не более '
        f'{SECOND_NAME_MAX_LENGTH} символов.'
    )
    avatar = models.ImageField(
        'Фотография профиля', max_length=MAX_URL_SIZE, upload_to='avatars/',
        help_text=f'Загрузите изображение(до {MAX_SIZE_IMG}Мб) для аватарки.',
        null=True, default=None,
        validators=[validate_image_size]
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

    def delete_avatar(self):
        delete_file(self.avatar)

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = User.objects.filter(
                pk=self.pk).only('avatar').first()
            if old_instance and old_instance.avatar != self.avatar:
                old_instance.delete_avatar()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.delete_avatar()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:DESCRIPTION_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента', max_length=INGR_NAME_MAX_LENGTH,
        help_text='Название ингредиента.'
        f' Не более {INGR_NAME_MAX_LENGTH} символов.'
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=INGR_MUNIT_MAX_LENGTH,
        help_text='Единица измерения ингредиента.'
        f' Не более {INGR_MUNIT_MAX_LENGTH} символов.'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name.lower()[:DESCRIPTION_LENGTH]


class Tag(models.Model):
    name = models.CharField(
        'Название тега', max_length=TAG_NAME_MAX_LENGTH, unique=True,
        help_text=f'Уникальное название тега.'
        f' Не более {TAG_NAME_MAX_LENGTH} символов.'
    )
    slug = models.SlugField(
        'Идентификатор', max_length=TAG_SLUG_MAX_LENGTH, unique=True,
        help_text='Уникальный slug тега, состоящий из латинских букв, цифр и'
        f' подчеркиваний. Не более {TAG_SLUG_MAX_LENGTH} символов.'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeComponent', verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    image = models.ImageField(
        'Изображение блюда', upload_to='dishes/', max_length=MAX_URL_SIZE,
        help_text=f'Загрузите изображение рецепта(до {MAX_SIZE_IMG}Мб).',
        validators=[validate_image_size]
    )
    name = models.CharField(
        'Название рецепта',
        max_length=RECIPE_NAME_MAX_LENGTH,
        help_text=f'Название рецепта. Не более {RECIPE_NAME_MAX_LENGTH}'
    )
    text = models.TextField('Описание', help_text='Описание рецепта.')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления в минутах.',
        validators=[MinValueValidator(1), MaxValueValidator(32767)]
    )
    author = models.ForeignKey(
        User, verbose_name='Автор', on_delete=models.CASCADE,
        help_text='Пользователь добавивший рецепт'
    )

    def delete_image(self):
        delete_file(self.image)

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = Recipe.objects.filter(
                pk=self.pk).only('image').first()
            if old_instance and old_instance.image != self.image:
                old_instance.delete_image()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.delete_image()
        super().delete(*args, **kwargs)

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:DESCRIPTION_LENGTH]


class RecipeComponent(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    quantity = models.PositiveSmallIntegerField(
        'Количество ингредиента', validators=[MinValueValidator(1)],
        help_text='Количество ингредиента'
    )

    class Meta:
        default_related_name = 'components'
        verbose_name = 'Компонент блюда'
        verbose_name_plural = 'Компоненты блюд'
        ordering = ('recipe',)

    def __str__(self):
        return f'{self.ingredient.name[:DESCRIPTION_LENGTH]} ({self.quantity})'


def delete_file(file_field):
    if file_field:
        try:
            file_field.delete(save=False)
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
