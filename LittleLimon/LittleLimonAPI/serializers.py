from rest_framework import serializers 
from . import models
from decimal import Decimal
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MenueItem
        category = CategorySerializer()
        fields = fields = ['id', 'title', 'price', 'featured', 'category']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = '__all__'

class CartSerializerDTO(serializers.ModelSerializer):
    class Meta:
        model = models.Cart
        fields = ['menuitem', 'unit_price', 'quantity',]


# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Order
#         fields = '__all__'

# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.OrderItem
#         fields = '__all__'   

class OrderItemSerializer(serializers.ModelSerializer):
    # menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = models.OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')

    class Meta:
        model = models.Order
        fields = ['id', 'user', 'delivery_crew', 'total', 'status','date', 'order_items']