from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Cart, ShippingAddress, Order, Transaction

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_cart_and_address(sender, instance, created, **kwargs):
    if created:
        # Create a cart for the new user
        Cart.objects.create(user=instance)
        # Create a default shipping address (empty) for the new user
        ShippingAddress.objects.create(
            user=instance,
            address='',
            current_address=True
        )

@receiver(post_save, sender=Order)
def update_transaction_on_order_creation(sender, instance, created, **kwargs):
    if created and instance.payment_status == 'Paid':
        # Update the associated transaction with the order reference
        Transaction.objects.filter(checkout_id=instance.order_id).update(order=instance)