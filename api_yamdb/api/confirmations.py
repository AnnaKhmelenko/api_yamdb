# Дополнительный файл для функций генерации кода подтверждения.
# Используется в нескольких файлах, поэтому вынесен отдельно.
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

from api_yamdb.settings import CHARS

User = get_user_model()


def get_confirmation_code():
    """Генерирует код подтверждения."""

    chars = CHARS  # Символы (лежат в настройках)
    return get_random_string(20, chars)


def send_confirmation_code(request):
    """Отправляет сгенерированный код подтверждения пользователю."""

    user = get_object_or_404(
        User,
        username=request.data.get('username'),
    )
    user.confirmation_code = get_confirmation_code()
    user.save()
    send_mail(
        'данные для получеия токена',
        f'Код подтверждения {user.confirmation_code}',
        'token@fakeyamdb.ru',
        [request.data.get('email')],
    )
