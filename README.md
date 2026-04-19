# Дипломный проект: Сервис автоматизации закупок (Финальная версия)

## Описание
Backend-приложение на Django REST Framework для автоматизации B2B закупок.

## Технологии
- **Python 3.13 / Django 4.2**
- **Django REST Framework**
- **PostgreSQL** (БД в Docker)
- **Celery & Redis** (Асинхронные задачи: импорт и email)
- **Docker & Docker Compose**

## Схема API
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/v1/user/register/confirm` | Подтверждение Email (активация) |
| GET/PATCH | `/api/v1/partner/state` | Управление приемом заказов магазином |
| GET | `/api/v1/partner/orders` | Список заказов для поставщика |
| DELETE | `/api/v1/basket` | Удаление позиций из корзины |
| GET | `/api/v1/order/<id>` | Детали конкретного заказа |

## Запуск проекта
1. `docker-compose up --build -d`
2. `docker-compose exec web python manage.py migrate`

## Тестирование
```bash
python manage.py test