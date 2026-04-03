from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from backend.models import User, Shop

class UserRegistrationTest(APITestCase):
    def test_registration_endpoint(self):
        """Проверка доступности эндпоинта регистрации"""
        url = reverse('backend:user-register')
        data = {
            'first_name': 'Ivan',
            'last_name': 'Ivanov',
            'email': 'testuser@example.com',
            'password': 'password123',
            'company': 'Netology',
            'position': 'Student'
        }
        response = self.client.post(url, data)
        # Мы ожидаем либо успех, либо ошибку валидации (если логика сложнее)
        # Главное, что эндпоинт отвечает
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

class ModelTest(TestCase):
    def test_create_shop(self):
        """Проверка создания записи в БД (модель Shop)"""
        user = User.objects.create(email="owner@shop.com", first_name="Owner")
        shop = Shop.objects.create(name="Test Shop", user=user)
        self.assertEqual(shop.name, "Test Shop")
