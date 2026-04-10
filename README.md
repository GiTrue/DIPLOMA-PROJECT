# Дипломный проект: Сервис автоматизации закупок

## Описание
Backend-приложение для автоматизации процесса закупок, реализованное на Django REST Framework. Позволяет магазинам загружать прайс-листы, а покупателям — формировать заказы.

## Основные возможности
- Регистрация и авторизация пользователей (Token Authentication).
- Подтверждение Email через систему токенов.
- Импорт товаров из YAML-файлов в фоновом режиме (Celery).
- Управление корзиной и оформление заказов.
- Административная панель для управления данными.

## Технологии
- **Python 3.13** / **Django 4.2**
- **Django REST Framework**
- **Celery** (очереди задач)
- **Redis** (брокер сообщений)
- **SQLite** (база данных)

## Установка и запуск (Локально)

1. Клонируйте репозиторий:
   ```bash
   git clone <ссылка_на_ваш_репозиторий>
   cd diploma_project
   
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   
3. Выполните миграции:
   ```bash
   python manage.py migrate
   
4. Запустите Redis (должен быть установлен в системе):
    ```bash
	redis-server
	
5. В отдельных терминалах запустите сервер и Celery:
    ```bash
    # Терминал 1: Django
    python manage.py runserver

    # Терминал 2: Celery
    celery -A core worker -l info
	
## Тестирование импорта
Для проверки импорта используйте команду curl (замените TOKEN на ваш):
    ```bash

	curl -X POST [http://127.0.0.1:8000/api/v1/partner/update](http://127.0.0.1:8000/api/v1/partner/update) \
     -H "Authorization: Token <ВАШ_ТОКЕН>" \
     -H "Content-Type: application/json" \
     -d '{"url": "[https://raw.githubusercontent.com/netology-code/python-final-diplom/refs/heads/master/data/shop1.yaml](https://raw.githubusercontent.com/netology-code/python-final-diplom/refs/heads/master/data/shop1.yaml)"}'
	 
## Тесты
# Запуск автоматических тестов:
    ```bash
	python manage.py test