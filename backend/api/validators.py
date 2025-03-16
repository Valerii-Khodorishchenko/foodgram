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


def validate_unique_items(items, item_name):
    if not items:
        raise ValidationError(f'Поле {item_name} не может быть пустым.')
    names = [
        item['id'].name if isinstance(
            item, dict
        ) else item.name for item in items
    ]
    duplicate_items = set([item for item in names if names.count(item) > 1])
    if duplicate_items:
        duplicate_items_str = [str(item) for item in duplicate_items]
        raise ValidationError(
            '{} не должны повторяться. Повторяющиеся {}: {}'.format(
                item_name, item_name.lower(), duplicate_items_str
            )
        )
    return items


def validate_products(products):
    return validate_unique_items(products, 'Продукты')


def validate_tags(tags):
    return validate_unique_items(tags, 'Теги')
