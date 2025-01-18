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


def validate_new_password(current_password, new_password):
    if current_password == new_password:
        raise ValidationError({
            'new_password': 'Новый пароль не может быть таким же, как текущий.'
        })
    return new_password


def validate_user_credentials(email, password):
    if not (user := authenticate(email=email, password=password)):
        raise ValidationError({'error': 'Неверный email или пароль'})
    return user

def validate_image_size(image):
    if image.size > MAX_SIZE_IMG * 1024 * 1024:
        raise ValidationError(
            f"Размер изображения не может превышать {MAX_SIZE_IMG} МБ."
        )

