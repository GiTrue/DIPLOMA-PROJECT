from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from backend.models import (
    User, Shop, Category, Product, ProductInfo, 
    Parameter, ProductParameter, Order, OrderItem, 
    Contact, ConfirmEmailToken
)

class CustomUserCreationForm(forms.ModelForm):
    """
    Специальная форма для создания пользователя в админке
    """
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'type')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Хешируем пароль
        if commit:
            user.save()
        return user

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm # Используем нашу форму для создания
    
    # Поля, которые запрашиваются при СОЗДАНИИ (add)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'type'),
        }),
    )

    # Поля, которые видны при РЕДАКТИРОВАНИИ (change)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'company', 'position', 'type')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'type')
    list_filter = ('type', 'is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)

# Регистрация остальных моделей остается без изменений
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'state')
    list_editable = ('state',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'model', 'shop', 'quantity', 'price', 'price_rrc')

@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dt', 'state')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info', 'quantity')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'phone')

@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at')
    readonly_fields = ('key', 'created_at')