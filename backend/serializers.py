from rest_framework import serializers
from backend.models import User, Category, Shop, ProductInfo, Product, ProductParameter, OrderItem, Order, Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {'user': {'write_only': True}}

class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()
    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)

class ProductInfoSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    category = serializers.StringRelatedField(source='product.category')
    product_parameters = ProductParameterSerializer(read_only=True, many=True)
    shop = serializers.StringRelatedField()

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'category', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {'order': {'write_only': True}}

class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(read_only=True, many=True)
    total_sum = serializers.IntegerField(read_only=True)
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact',)
        read_only_fields = ('id',)