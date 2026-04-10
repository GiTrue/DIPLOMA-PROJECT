import os
from celery import Celery

# Указываем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Загружаем настройки из файла settings.py с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический поиск задач tasks.py в приложениях
app.autodiscover_tasks()