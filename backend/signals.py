import binascii
import os
from django.dispatch import receiver
from django.db.models.signals import post_save
from backend.models import User, ConfirmEmailToken
from backend.tasks import send_email_task

@receiver(post_save, sender=User)
def newUser_token_created(sender, instance, created, **kwargs):
    """
    Создание токена и отправка письма при регистрации
    """
    if created:
        # Генерируем уникальный ключ вручную, если модель капризничает
        new_key = binascii.hexlify(os.urandom(20)).decode()
        
        # Используем update_or_create вместо get_or_create для надежности
        token, created_token = ConfirmEmailToken.objects.update_or_create(
            user=instance,
            defaults={'key': new_key}
        )
        
        # Отправляем задачу в Celery
        send_email_task.delay(
            subject=f"Confirm registration for {instance.email}",
            message=f"Your confirmation token: {token.key}",
            to_email=instance.email
        )