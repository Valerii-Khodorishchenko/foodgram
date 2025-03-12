from django.core.exceptions import ValidationError


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
