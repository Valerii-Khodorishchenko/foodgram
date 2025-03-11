import re

from django.core.exceptions import ValidationError


class MaximumLengthPasswordValidator:
    def __init__(self, max_length=128):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(self.get_help_text())

    def get_help_text(self):
        return 'Длина пароля не должна превышать {} символов.'.format(
            self.max_length
        )


def validate_username(username):
    if invalid_chars := re.sub(r'[\w.@+-]', '', username):
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы: {}.'.format(
                ' '.join(set(invalid_chars))
            )
        )
    return username


def validate_image(image):
    if image is None:
        raise ValidationError('Недолжно быть пустым')
    return image


def validate_subscribe(data, user, target_user, method):
    if user == target_user:
        raise ValidationError('Нельзя подписаться на себя.')
    if method == 'POST':
        if target_user.following.filter(user=user).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')
    elif method == 'DELETE':
        if not user.followers.filter(following=target_user).exists():
            raise ValidationError('Вы не подписаны на этого пользователя.')
    return data


def validate_required_fields(data, fields):
    missing_fields = [field for field in fields if not data.get(field)]
    if missing_fields:
        raise ValidationError(
            {field: 'Обязательное поле.' for field in missing_fields})


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
        if recipe.favorited_by.filter(user=user).exists():
            raise ValidationError('Рецепт уже в избранном.')
    else:
        if not recipe.favorited_by.filter(user=user).exists():
            raise ValidationError('Рецепт отсутствует в избранном.')


def validate_cart(user, recipe, method):
    if method == 'POST':
        if recipe.in_carts.filter(user=user).exists():
            raise ValidationError('Рецепт уже в списке покупок.')
    else:
        if not recipe.in_carts.filter(user=user).exists():
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
