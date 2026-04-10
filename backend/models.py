from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),
)

STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    username = None
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"

    def __str__(self):
        return self.email

class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Пользователь', blank=True, null=True, on_delete=models.CASCADE, related_name='shop')
    state = models.BooleanField(verbose_name='статус получения заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"

    def __str__(self):
        return self.name

class ProductInfo(models.Model):
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Список информации о продуктах"
        constraints = [models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info')]

    def __str__(self):
        return f"{self.product.name} ({self.model})"

class Parameter(models.Model):
    name = models.CharField(max_length=40, verbose_name='Название')
    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = "Список параметров"

    def __str__(self):
        return self.name

class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, related_name='product_parameters', on_delete=models.CASCADE, verbose_name='Информация о продукте')
    parameter = models.ForeignKey(Parameter, related_name='product_parameters', on_delete=models.CASCADE, verbose_name='Параметр')
    value = models.CharField(verbose_name='Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр продукта'
        verbose_name_plural = "Список параметров продуктов"

class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='contacts', on_delete=models.CASCADE)
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=10, blank=True, verbose_name='Дом')
    structure = models.CharField(max_length=10, blank=True, verbose_name='Корпус')
    building = models.CharField(max_length=10, blank=True, verbose_name='Строение')
    apartment = models.CharField(max_length=10, blank=True, verbose_name='Квартира')
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов"

    def __str__(self):
        return f"{self.city}, {self.street} ({self.phone})"

class Order(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='orders', on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    state = models.CharField(choices=STATE_CHOICES, max_length=15, verbose_name='Статус')
    contact = models.ForeignKey(Contact, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Контакт')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"

    def __str__(self):
        return f"Заказ №{self.id} от {self.dt.strftime('%d.%m.%Y')}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='ordered_items', on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте', related_name='ordered_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')

    class Meta:
        verbose_name = 'Позиция в заказе'
        verbose_name_plural = "Список позиций в заказе"

class ConfirmEmailToken(models.Model):
    user = models.ForeignKey(User, related_name='confirm_email_tokens', on_delete=models.CASCADE, verbose_name='Пользователь')
    key = models.CharField(max_length=64, db_index=True, unique=True, verbose_name='Ключ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = "Токены подтверждения Email"