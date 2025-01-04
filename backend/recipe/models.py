from django.contrib.auth.models import AbstractUser
from django.db import models

from recipe.constants import (
    DESCRIPTION_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    SECOND_NAME_MAX_LENGTH,
    USERNAME_MAX_LENGTH
)
from recipe.validators import validate_username


class Recipe(models.Model):
    pass


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
        Recipe, verbose_name='Избранные рецепты', related_name='favorites'
    )
    cart = models.ManyToManyField(
        Recipe, verbose_name='Корзина', related_name='cart'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:DESCRIPTION_LENGTH]
