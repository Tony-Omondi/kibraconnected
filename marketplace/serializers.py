from rest_framework import serializers
from .models import Category, Product, Order, Cart, CartItem
from accounts.models import User
from accounts.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    seller_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='seller', write_only=True
    )
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, allow_null=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_id', 'title', 'description',
            'price', 'image', 'category', 'category_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    buyer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='buyer', write_only=True
    )
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'buyer_id', 'product', 'product_id', 'ordered_at'
        ]
        read_only_fields = ['id', 'ordered_at']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']
        read_only_fields = ['id']

class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']