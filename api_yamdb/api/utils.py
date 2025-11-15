import uuid

from django.conf import settings
from django.core.mail import send_mail


def send_confirmation_email(user):
    """Отправляет email с кодом подтверждения."""

    confirmation_code = str(uuid.uuid4())
    user.confirmation_code = confirmation_code
    user.save()

    subject = 'Код подтверждения'
    message = f'Ваш код подтверждения: {confirmation_code}'
    recipient_list = [user.email]

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')

    send_mail(subject, message, from_email, recipient_list)
