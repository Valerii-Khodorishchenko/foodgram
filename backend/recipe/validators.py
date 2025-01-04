import re

from django.core.exceptions import ValidationError


def validate_username(username):
    if invalid_chars := re.sub(r'[\w.@+-]', '', username):
        raise ValidationError(
            'Имя пользователя содержит недопустимые символы:'
            f' {" ".join(set(invalid_chars))}.'
        )
    return username
