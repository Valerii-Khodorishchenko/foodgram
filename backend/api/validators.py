from django.core.exceptions import ValidationError


def validate_image(image):
    if image is None:
        raise ValidationError('Недолжно быть пустым')
    return image


def validate_required_fields(data, fields):
    missing_fields = [field for field in fields if not data.get(field)]
    if missing_fields:
        raise ValidationError(
            {field: 'Обязательное поле.' for field in missing_fields})


def validate_products(products):
    if not products:
        raise ValidationError('Поле не может быть пустым.')
    unique_products = {product['id'] for product in products}
    if len(products) != len(unique_products):
        raise ValidationError('Ингредиенты не должны повторяться.')
    return products


def validate_tags(tags):
    if not tags:
        raise ValidationError('Поле не может быть пустым.')
    unique_tags = {tag.id for tag in tags}
    if len(tags) != len(unique_tags):
        raise ValidationError(
            'Теги не должны повторяться.'
        )
    return tags
