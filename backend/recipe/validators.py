import re

from django.core.exceptions import ValidationError

from backend.settings import MAX_PASSWORD_LENGTH


class MaximumLengthPasswordValidator:
    def __init__(self, max_length=MAX_PASSWORD_LENGTH):
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
