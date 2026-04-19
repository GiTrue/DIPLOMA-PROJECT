import binascii
import os
import yaml
from django.http import JsonResponse
from django.db.models import Q, Sum, F
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from backend.tasks import do_import_task 
from backend.models import (
    Shop, Category, ProductInfo, Product, Parameter, 
    ProductParameter, Order, OrderItem, Contact, User, ConfirmEmailToken
)
from backend.serializers import (
    ProductInfoSerializer, OrderSerializer, 
    ContactSerializer, OrderItemSerializer
)

class RegisterAccount(APIView):
    """Регистрация пользователя"""
    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'company', 'position'}.issubset(request.data):
            try:
                validate_password(request.data['password'])
            except Exception as password_error:
                return Response({'status': False, 'error': {'password': password_error.messages}}, status=400)
            
            if User.objects.filter(email=request.data['email']).exists():
                return Response({'status': False, 'error': 'Пользователь уже существует'}, status=400)

            user = User.objects.create_user(
                email=request.data['email'],
                password=request.data['password'],
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                company=request.data['company'],
                position=request.data['position'],
                is_active=False
            )
            user.save()
            return Response({'status': True, 'message': 'Пользователь зарегистрирован.'}, status=201)
        return Response({'status': False, 'error': 'Не указаны все аргументы'}, status=400)

class ConfirmAccount(APIView):
    """Активация аккаунта по токену"""
    def post(self, request, *args, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'status': True})
            return Response({'status': False, 'error': 'Неверный токен или email'}, status=400)
        return Response({'status': False, 'error': 'Не переданы email и токен'}, status=400)

class PartnerState(APIView):
    """Управление статусом магазина"""
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'status': False, 'error': 'Только для магазинов'}, status=403)
        return Response({'status': True, 'state': request.user.shop.state})

    def patch(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'status': False, 'error': 'Только для магазинов'}, status=403)
        state = request.data.get('state')
        if state is not None:
            Shop.objects.filter(user_id=request.user.id).update(state=state)
            return Response({'status': True})
        return Response({'status': False, 'error': 'Не указан параметр state'}, status=400)

class PartnerOrders(APIView):
    """Список заказов для поставщика"""
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'status': False, 'error': 'Только для магазинов'}, status=403)
        orders = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id).exclude(state='basket').distinct()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class PartnerUpdate(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'status': False, 'error': 'Только для магазинов'}, status=403)
        url = request.data.get('url')
        if url:
            do_import_task.delay(user_id=request.user.id, url=url)
            return JsonResponse({'status': True})
        return JsonResponse({'status': False, 'error': 'Не указан URL'}, status=400)

class BasketView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        basket = Order.objects.filter(user_id=request.user.id, state='basket').first()
        if not basket:
            return Response({'status': True, 'items': []})
        serializer = OrderSerializer(basket)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        items_dict = request.data.get('items')
        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
        for item in items_dict:
            item.update({'order': basket.id})
            serializer = OrderItemSerializer(data=item)
            if serializer.is_valid(): serializer.save()
        return Response({'status': True})

    def delete(self, request, *args, **kwargs):
        """Удаление из корзины"""
        items_ids = request.data.get('items')
        if not items_ids:
            return Response({'status': False, 'error': 'Не переданы ID'}, status=400)
        OrderItem.objects.filter(order__user_id=request.user.id, order__state='basket', id__in=items_ids).delete()
        return Response({'status': True})

class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        """Детали заказа по ID"""
        order_id = kwargs.get('id')
        if order_id:
            order = Order.objects.filter(user_id=request.user.id, id=order_id).first()
            if not order: return Response({'status': False, 'error': 'Не найден'}, status=404)
            return Response(OrderSerializer(order).data)
        orders = Order.objects.filter(user_id=request.user.id).exclude(state='basket')
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request, *args, **kwargs):
        contact_id = request.data.get('contact_id')
        updated = Order.objects.filter(user_id=request.user.id, state='basket').update(contact_id=contact_id, state='new')
        if updated: return Response({'status': True})
        return Response({'status': False, 'error': 'Корзина пуста'}, status=400)

class ProductInfoView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = ProductInfo.objects.filter(shop__state=True).select_related('shop', 'product__category').distinct()
        return Response(ProductInfoSerializer(queryset, many=True).data)

class ContactView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        contacts = Contact.objects.filter(user_id=request.user.id)
        return Response(ContactSerializer(contacts, many=True).data)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ContactSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True})
        return Response({'status': False, 'errors': serializer.errors}, status=400)