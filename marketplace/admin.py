from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Cart, CartItem, Coupon, ShippingAddress, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'seller', 'price', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'seller__username', 'seller__email')
    ordering = ('-created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'buyer', 'get_order_items', 'grand_total', 'payment_status', 'ordered_at')
    list_filter = ('payment_status', 'ordered_at')
    search_fields = ('order_id', 'buyer__username', 'buyer__email')
    ordering = ('-ordered_at',)

    def get_order_items(self, obj):
        return ", ".join([f"{item.product.title} (x{item.quantity})" for item in obj.order_items.all()])
    get_order_items.short_description = 'Items'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'product_price')
    search_fields = ('order__order_id', 'product__title')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_price', 'get_total_price_after_coupon', 'created_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)

    def get_total_price(self, obj):
        return obj.total_price
    get_total_price.short_description = 'Total Price'

    def get_total_price_after_coupon(self, obj):
        return obj.total_price_after_coupon
    get_total_price_after_coupon.short_description = 'Total After Coupon'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'get_total_price')
    search_fields = ('cart__user__username', 'cart__user__email', 'product__title')

    def get_total_price(self, obj):
        return obj.total_price
    get_total_price.short_description = 'Total Price'

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_code', 'discount_amount', 'is_expired', 'valid_from', 'valid_to')
    list_filter = ('is_expired', 'valid_from', 'valid_to')
    search_fields = ('coupon_code',)

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'current_address')
    list_filter = ('current_address',)
    search_fields = ('user__username', 'user__email', 'address')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'checkout_id', 'amount', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('order__order_id', 'checkout_id')