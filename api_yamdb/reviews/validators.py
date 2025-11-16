import re
from datetime import datetime

from django.core.exceptions import ValidationError


def validate_username(value):
    """Валидация имени пользователя."""
    if value.lower() == 'me':
        raise ValidationError('Имя пользователя "me" не разрешено.')

    invalid_chars = re.sub(r'[\w.@+-]', '', value)
    if invalid_chars:
        raise ValidationError(
            f'Недопустимые символы в имени пользователя: {invalid_chars}'
        )
    return value


def validate_year(value):
    """Валидация года выпуска."""
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError('Год выпуска не может быть в будущем.')
    return value
