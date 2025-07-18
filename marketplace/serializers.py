from rest_framework import serializers
from .models import Category, Product, Order, Cart, CartItem, Coupon, ShippingAddress, OrderItem, Transaction
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

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'coupon_code', 'discount_amount', 'minimum_amount', 'is_expired', 'valid_from', 'valid_to']
        read_only_fields = ['id']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'user', 'address', 'current_address']
        read_only_fields = ['id', 'user']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True, allow_null=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'product_price']
        read_only_fields = ['id', 'product_price']

class OrderSerializer(serializers.ModelSerializer):
    buyer = UserSerializer(read_only=True)
    buyer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='buyer', write_only=True
    )
    coupon = CouponSerializer(read_only=True)
    coupon_id = serializers.PrimaryKeyRelatedField(
        queryset=Coupon.objects.all(), source='coupon', write_only=True, allow_null=True
    )
    order_items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = serializers.CharField(max_length=255, allow_blank=True)

    class Meta:
        model = Order
        fields = [
            'id', 'buyer', 'buyer_id', 'order_id', 'ordered_at', 'payment_status',
            'payment_mode', 'shipping_address', 'order_total_price', 'coupon',
            'coupon_id', 'grand_total', 'order_items'
        ]
        read_only_fields = ['id', 'ordered_at', 'order_id', 'payment_status', 'payment_mode', 'order_total_price', 'grand_total', 'order_items']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']
        read_only_fields = ['id', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()

class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    coupon = CouponSerializer(read_only=True)
    coupon_id = serializers.PrimaryKeyRelatedField(
        queryset=Coupon.objects.all(), source='coupon', write_only=True, allow_null=True
    )
    total_price = serializers.SerializerMethodField()
    total_price_after_coupon = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'created_at', 'is_paid', 'payment_reference',
            'coupon', 'coupon_id', 'total_price', 'total_price_after_coupon'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'is_paid', 'payment_reference', 'total_price', 'total_price_after_coupon']

    def get_total_price(self, obj):
        return obj.get_cart_total()

    def get_total_price_after_coupon(self, obj):
        return obj.get_cart_total_after_coupon()

class TransactionSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source='order', write_only=True, allow_null=True
    )

    class Meta:
        model = Transaction
        fields = ['id', 'order', 'order_id', 'amount', 'checkout_id', 'status', 'timestamp']
        read_only_fields = ['id', 'timestamp']