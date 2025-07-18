from django.db import models
from django.conf import settings
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_expired = models.BooleanField(default=False)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.coupon_code

class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipping_addresses')
    address = models.TextField()
    current_address = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.address[:50]}"

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')

    def __str__(self):
        return f"Cart for {self.user.email}"

    def get_cart_total(self):
        """Calculate the total price of all cart items."""
        return sum(item.get_total_price() for item in self.items.all())

    def get_cart_total_after_coupon(self):
        """Calculate the total price after applying the coupon, if applicable."""
        total = self.get_cart_total()
        if self.coupon and total >= self.coupon.minimum_amount and not self.coupon.is_expired:
            total -= self.coupon.discount_amount
        return max(total, 0)  # Ensure total doesn't go negative

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} of {self.product.title} in cart"

    def get_total_price(self):
        """Calculate the total price for this cart item."""
        return self.product.price * self.quantity

class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=100, default=uuid.uuid4)
    ordered_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Failed', 'Failed')],
        default='Pending'
    )
    payment_mode = models.CharField(max_length=100, default='Paystack')
    shipping_address = models.TextField(blank=True, null=True)
    order_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return f"Order {self.order_id} by {self.buyer.email}"

    def get_order_total_price(self):
        """Calculate the total price of all order items."""
        return sum(item.get_total_price() for item in self.order_items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.title if self.product else 'Deleted Product'} in order {self.order.order_id}"

    def get_total_price(self):
        """Calculate the total price for this order item."""
        return self.product_price * self.quantity

class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.checkout_id} - {self.amount}"