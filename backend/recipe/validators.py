import re

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from recipe.constants import MAX_SIZE_IMG


def validate_username(username):
    if invalid_chars := re.sub(r'[\w.@+-]', '', username):
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы:'
            f' {" ".join(set(invalid_chars))}.'
        )
    return username


def validate_current_password(user, current_password):
    if not user.check_password(current_password):
        raise ValidationError('Неверный текущий пароль')
    return current_password


def validate_new_password(passwords):
    if passwords['new_password'] == passwords['current_password']:
        raise ValidationError({
            'new_password': 'Новый пароль не может быть таким же, как текущий.'
        })
    return passwords


def validate_user_credentials(data):
    if not (user := authenticate(
        email=data.get('email'), password=data.get('password')
    )):
        raise ValidationError({'error': 'Неверный email или пароль'})
    return user


def validate_image_size(image):
    if image and image.size > MAX_SIZE_IMG * 1024 * 1024:
        raise ValidationError(
            f'Размер изображения не может превышать {MAX_SIZE_IMG} МБ.'
        )
    return image


def validate_subscribe(data, user, target_user, method):
    if user == target_user:
        raise ValidationError('Нельзя подписаться на себя.')
    if method == 'POST':
        if user.followings.filter(id=target_user.id).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')
    elif method == 'DELETE':
        if not user.followings.filter(id=target_user.id).exists():
            raise ValidationError('Вы не подписаны на этого пользователя.')
    return data


def validate_required_fields(data, fields):
    for field in fields:
        if not data.get(field):
            raise ValidationError({field: 'Обязательное поле.'})


def validate_ingredients(ingredients):
    if not ingredients:
        raise ValidationError('Поле не может быть пустым.')
    unique_ingredients = {ingredient['id'] for ingredient in ingredients}
    if len(ingredients) != len(unique_ingredients):
        raise ValidationError('Ингредиенты не должны повторяться.')
    return ingredients


def validate_tags(tags):
    if not tags:
        raise ValidationError('Поле не может быть пустым.')
    unique_tags = {tag.id for tag in tags}
    if len(tags) != len(unique_tags):
        raise ValidationError(
            'Теги не должны повторяться.'
        )
    return tags


def validate_favorite(user, recipe, method):
    if method == 'POST':
        if user.favorites.filter(id=recipe.id).exists():
            raise ValidationError('Рецепт уже в избранном.')
    else:
        if not user.favorites.filter(id=recipe.id).exists():
            raise ValidationError('Рецепт отсутствует в избранном.')


def validate_cart(user, recipe, method):
    if method == 'POST':
        if user.cart.filter(id=recipe.id).exists():
            raise ValidationError('Рецепт уже в списке покупок.')
    else:
        if not user.cart.filter(id=recipe.id).exists():
            raise ValidationError('Рецепт отсутствует в списке покупок.')


def validate_favorite_or_cart(context, category):
    user = context['request'].user
    recipe = context['recipe']
    method = context['request'].method
    if category == 'favorite':
        validate_favorite(user, recipe, method)
    elif category == 'cart':
        validate_cart(user, recipe, method)
    else:
        raise ValidationError('Неверная категория.')
    return recipe
