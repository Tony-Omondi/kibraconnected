import requests
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import redirect
from .models import Category, Product, Order, Cart, CartItem, Coupon, ShippingAddress, OrderItem, Transaction
from .serializers import (
    CategorySerializer, ProductSerializer, OrderSerializer, CartSerializer,
    CartItemSerializer, CouponSerializer, ShippingAddressSerializer, OrderItemSerializer
)

# Paystack Configuration
PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY
PAYSTACK_INITIALIZE_URL = 'https://api.paystack.co/transaction/initialize'
PAYSTACK_VERIFY_URL = 'https://api.paystack.co/transaction/verify/'

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user if hasattr(obj, 'seller') else obj.buyer == request.user

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'])
    def apply_coupon(self, request):
        cart = Cart.objects.get(user=request.user, is_paid=False)
        coupon_code = request.data.get('coupon_code')
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code, is_expired=False)
            if cart.get_cart_total() < coupon.minimum_amount:
                return Response(
                    {'error': f'Minimum order amount is {coupon.minimum_amount}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if cart.coupon:
                return Response(
                    {'error': 'Coupon already applied'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart.coupon = coupon
            cart.save()
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired coupon'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def remove_coupon(self, request, pk=None):
        cart = Cart.objects.get(user=request.user, is_paid=False)
        cart.coupon = None
        cart.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
            item, created = CartItem.objects.get_or_create(
                cart=cart, product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                item.quantity += quantity
                item.save()
            return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        try:
            item = CartItem.objects.get(cart=cart, product_id=product_id)
            item.delete()
            return Response({'status': 'item removed'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'item not in cart'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def update_item_quantity(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))
        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            if quantity < 1:
                return Response(
                    {'error': 'Quantity must be at least 1'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity = quantity
            item.save()
            return Response(CartItemSerializer(item).data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def initiate_payment(self, request, pk=None):
        cart = self.get_object()
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        amount = int(cart.get_cart_total_after_coupon() * 100)  # Convert to kobo
        email = request.user.email
        # Use deep link for mobile, HTTP for web
        is_mobile = 'Mobile' in request.META.get('HTTP_USER_AGENT', '')
        callback_url = 'kibraconnect://payment-callback' if is_mobile else request.build_absolute_uri('/api/payments/callback/')

        headers = {
            'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            'email': email,
            'amount': amount,
            'callback_url': callback_url,
            'metadata': {
                'cart_id': str(cart.id),
                'custom_fields': [
                    {
                        'display_name': 'Cart Items',
                        'variable_name': 'cart_items',
                        'value': ', '.join([item.product.title for item in cart.items.all()])
                    }
                ]
            }
        }

        try:
            response = requests.post(PAYSTACK_INITIALIZE_URL, headers=headers, json=data)
            response_data = response.json()
            if response.status_code == 200 and response_data['status']:
                cart.payment_reference = response_data['data']['reference']
                cart.save()
                return Response({
                    'status': 'success',
                    'authorization_url': response_data['data']['authorization_url'],
                    'reference': response_data['data']['reference']
                }, status=status.HTTP_200_OK)
            return Response(
                {'error': response_data.get('message', 'Payment initialization failed')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-ordered_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

class PaymentCallbackView(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def callback(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response(
                {'error': 'No reference provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        headers = {
            'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.get(f'{PAYSTACK_VERIFY_URL}{reference}', headers=headers)
            response_data = response.json()
            if response.status_code == 200 and response_data['status'] and response_data['data']['status'] == 'success':
                cart_id = response_data['data']['metadata']['cart_id']
                cart = Cart.objects.get(id=cart_id, is_paid=False)

                # Create transaction record
                Transaction.objects.create(
                    order=None,
                    amount=cart.get_cart_total_after_coupon(),
                    checkout_id=reference,
                    status='Success'
                )

                # Create order
                order = Order.objects.create(
                    buyer=cart.user,
                    order_id=reference,
                    payment_status='Paid',
                    payment_mode='Paystack',
                    shipping_address=cart.user.shipping_addresses.filter(current_address=True).first().address
                        if cart.user.shipping_addresses.filter(current_address=True).exists() else '',
                    order_total_price=cart.get_cart_total(),
                    coupon=cart.coupon,
                    grand_total=cart.get_cart_total_after_coupon()
                )

                # Create order items
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        product_price=cart_item.product.price
                    )

                # Update transaction with order
                Transaction.objects.filter(checkout_id=reference).update(order=order)

                # Mark cart as paid
                cart.is_paid = True
                cart.save()

                # Redirect to mobile deep link for mobile clients
                is_mobile = 'Mobile' in request.META.get('HTTP_USER_AGENT', '')
                if is_mobile:
                    return redirect(f'kibraconnect://payment-callback?reference={reference}')
                return Response({
                    'status': 'success',
                    'order_id': order.order_id
                }, status=status.HTTP_200_OK)
            return Response(
                {'error': response_data.get('message', 'Payment verification failed')},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            Transaction.objects.create(
                order=None,
                amount=0,
                checkout_id=reference,
                status='Failed'
            )
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )