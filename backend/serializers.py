from rest_framework import serializers
from backend.models import User, Category, Shop, ProductInfo, Product, ProductParameter, OrderItem, Order, Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building', 'apartment', 'user', 'phone')
        extra_kwargs = {'user': {'write_only': True}}

class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(read_only=True, many=True)
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company', 'position', 'contacts')

class ProductInfoSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    category = serializers.CharField(source='product.category.name', read_only=True)
    
    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'category', 'shop', 'quantity', 'price', 'price_rrc')

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order')
        extra_kwargs = {'order': {'write_only': True}}

class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemSerializer(many=True, read_only=True)
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact')

    def get_total_sum(self, obj):
        return obj.ordered_items.aggregate(
            total=Sum(F('quantity') * F('product_info__price'))
        )['total'] or 0