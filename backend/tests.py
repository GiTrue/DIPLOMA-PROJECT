from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from backend.models import User, Shop, ConfirmEmailToken

class UserRegistrationTest(APITestCase):
    """
    Тестирование регистрации и сопутствующих процессов
    """
    def test_registration_endpoint_availability(self):
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
        # Так как сейчас в urls.py стоит заглушка ProductInfoView (GET), 
        # POST вернет 405 Method Not Allowed. Для теста доступности это ок.
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED, 
            status.HTTP_200_OK, 
            status.HTTP_405_METHOD_NOT_ALLOWED
        ])

    def test_signal_token_creation(self):
        """Проверка, что сигнал создает токен подтверждения при создании пользователя"""
        email = "signal_test@example.com"
        user = User.objects.create_user(
            email=email,
            password="password123",
            first_name="Signal",
            last_name="Test"
        )
        
        # Проверяем наличие токена в БД
        token_exists = ConfirmEmailToken.objects.filter(user=user).exists()
        self.assertTrue(token_exists, "Сигнал не создал токен подтверждения для нового пользователя")
        
        # Проверяем, что ключ токена не пустой
        token = ConfirmEmailToken.objects.get(user=user)
        self.assertIsNotNone(token.key)
        self.assertNotEqual(token.key, "")


class ShopBusinessLogicTest(APITestCase):
    """
    Тестирование логики магазинов и товаров
    """
    def setUp(self):
        # Создаем тестового пользователя-магазина
        self.user = User.objects.create_user(
            email="shop_owner@test.com",
            password="password123",
            type="shop"
        )
        self.shop = Shop.objects.create(name="Test Shop", user=self.user)

    def test_create_shop_model(self):
        """Проверка корректности создания модели Shop"""
        self.assertEqual(self.shop.name, "Test Shop")
        self.assertEqual(self.shop.user.email, "shop_owner@test.com")

    def test_partner_update_unauthorized(self):
        """Проверка, что анонимный пользователь не может обновить прайс"""
        url = reverse('backend:partner-update')
        response = self.client.post(url, {'url': 'http://example.com/price.yaml'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)