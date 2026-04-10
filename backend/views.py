import yaml
import requests
from django.http import JsonResponse
from django.db.models import Q, Sum, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password

# Импортируем задачу Celery и модели
from backend.tasks import do_import_task 
from backend.models import (
    Shop, Category, ProductInfo, Product, Parameter, 
    ProductParameter, Order, OrderItem, Contact, User
)
from backend.serializers import (
    ProductInfoSerializer, OrderSerializer, 
    ContactSerializer, OrderItemSerializer
)

class RegisterAccount(APIView):
    """
    Класс для регистрации покупателей и магазинов
    """
    def post(self, request, *args, **kwargs):
        # Проверяем наличие обязательных аргументов
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            # Проверяем пароль на сложность
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return Response({'status': False, 'error': {'password': password_error.messages}})
            else:
                # Проверяем уникальность email
                user_serializer = ContactSerializer(data=request.data) # Используем подходящий сериализатор или создаем вручную
                
                # Создаем пользователя (сигнал в signals.py сработает автоматически)
                user = User.objects.create_user(
                    email=request.data['email'],
                    password=request.data['password'],
                    first_name=request.data['first_name'],
                    last_name=request.data['last_name'],
                    company=request.data['company'],
                    position=request.data['position'],
                    is_active=False  # Пользователь неактивен до подтверждения почты
                )
                user.save()
                return Response({'status': True, 'message': 'Пользователь зарегистрирован. Подтвердите email.'}, status=201)

        return Response({'status': False, 'error': 'Не указаны все необходимые аргументы'}, status=400)

class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от партнера
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'status': False, 'error': 'Только для магазинов'}, status=403)

        url = request.data.get('url')
        if url:
            if not hasattr(request.user, 'shop'):
                return JsonResponse({'status': False, 'error': 'У вашего пользователя не создан магазин'}, status=400)
            
            do_import_task.delay(user_id=request.user.id, url=url)
            return JsonResponse({'status': True})

        return JsonResponse({'status': False, 'error': 'Не указан URL'})

class ProductInfoView(APIView):
    def get(self, request, *args, **kwargs):
        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')
        if shop_id:
            query = query & Q(shop_id=shop_id)
        if category_id:
            query = query & Q(category_id=category_id)
        queryset = ProductInfo.objects.filter(query).select_related('shop', 'product__category').prefetch_related('product_parameters__parameter').distinct()
        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)

class BasketView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        basket = Order.objects.filter(user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))).first()
        if not basket:
            return Response({'status': True, 'message': 'Корзина пуста', 'items': []})
        serializer = OrderSerializer(basket)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        items_dict = request.data.get('items')
        if not items_dict:
            return Response({'status': False, 'error': 'Не переданы товары'})
        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
        for item in items_dict:
            item.update({'order': basket.id})
            serializer = OrderItemSerializer(data=item)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({'status': False, 'errors': serializer.errors})
        return Response({'status': True})

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        contact_id = request.data.get('contact_id')
        if not contact_id:
            return Response({'status': False, 'error': 'Не указан адрес (contact_id)'})
        updated_count = Order.objects.filter(user_id=request.user.id, state='basket').update(
            contact_id=contact_id, state='new')
        if updated_count:
            return Response({'status': True, 'message': 'Заказ сформирован'})
        return Response({'status': False, 'error': 'Корзина пуста'})

class ContactView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        contacts = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ContactSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True})
        return Response({'status': False, 'errors': serializer.errors})