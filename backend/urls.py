from django.urls import path
from backend.views import (
    ProductInfoView, BasketView, ContactView, OrderView, 
    PartnerUpdate, RegisterAccount, ConfirmAccount, PartnerState, PartnerOrders
)

app_name = 'backend'

urlpatterns = [
    path('user/register', RegisterAccount.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('partner/update', PartnerUpdate.as_view(), name='partner-update'),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
    path('partner/orders', PartnerOrders.as_view(), name='partner-orders'),
    path('products', ProductInfoView.as_view(), name='products'),
    path('basket', BasketView.as_view(), name='basket'),
    path('contact', ContactView.as_view(), name='contact'),
    path('order', OrderView.as_view(), name='order'),
    path('order/<int:id>', OrderView.as_view(), name='order-detail'),
]
