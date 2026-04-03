from django.db.models import Sum, F
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.models import ConfirmEmailToken, Shop, Category, ProductInfo, Order, OrderItem, Contact
from backend.serializers import UserSerializer, OrderSerializer, OrderItemSerializer, ContactSerializer
from backend.tasks import send_email_task, do_import_task

class RegisterAccount(APIView):
    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password'}.issubset(request.data):
            user_serializer = UserSerializer(data=request.data)
            if user_serializer.is_valid():
                user = user_serializer.save()
                user.set_password(request.data['password'])
                user.save()
                
                # Создаем токен и отправляем письмо через Celery
                token, _ = ConfirmEmailToken.objects.get_or_create(user=user)
                send_email_task.delay(
                    "Подтверждение регистрации",
                    f"Ваш токен: {token.key}",
                    user.email
                )
                return JsonResponse({'Status': True})
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})
        return JsonResponse({'Status': False, 'Errors': 'Не указаны все аргументы'})

class PartnerUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=403)
        
        url = request.data.get('url')
        if url:
            # Вызываем задачу импорта асинхронно
            do_import_task.delay(request.user.id, url)
            return JsonResponse({'Status': True, 'Message': 'Импорт запущен'})
            
        return JsonResponse({'Status': False, 'Errors': 'Не указан URL'})

# Остальные методы (BasketView, OrderView) остаются как в базе, 
# но вызов отправки письма при заказе также меняем на .delay()