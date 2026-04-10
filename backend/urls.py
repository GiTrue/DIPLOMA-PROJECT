from django.urls import path
from backend.views import (
    ProductInfoView, BasketView, ContactView, 
    OrderView, PartnerUpdate, RegisterAccount # Добавили импорт
)

app_name = 'backend'

urlpatterns = [
    # Теперь здесь реальный класс регистрации
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    
    path('products', ProductInfoView.as_view(), name='products'),
    path('basket', BasketView.as_view(), name='basket'),
    path('contact', ContactView.as_view(), name='contact'),
    path('order', OrderView.as_view(), name='order'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
]
