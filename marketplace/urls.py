from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, OrderViewSet, CartViewSet, CouponViewSet, ShippingAddressViewSet, PaymentCallbackView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'shipping-addresses', ShippingAddressViewSet, basename='shipping-address')
router.register(r'payments', PaymentCallbackView, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('carts/verify-payment/', CartViewSet.as_view({'get': 'verify_payment'}), name='cart-verify-payment'),
]