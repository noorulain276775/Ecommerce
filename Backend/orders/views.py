from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
import uuid
import logging

from .models import Order, OrderItem, Payment, OrderStatusHistory, Cart, CartItem
from .serializers import (
    OrderSerializer, CreateOrderSerializer, PaymentSerializer, CreatePaymentSerializer,
    CartSerializer, CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer
)
from products.models import Product

logger = logging.getLogger(__name__)


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's cart"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def post(self, request):
        """Add item to cart"""
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            
            cart, created = Cart.objects.get_or_create(user=request.user)
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            # Check inventory
            if hasattr(product, 'inventory') and product.inventory.stock < quantity:
                return Response(
                    {'error': 'Insufficient stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, item_id):
        """Update cart item quantity"""
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            # Check inventory
            if hasattr(cart_item.product, 'inventory') and cart_item.product.inventory.stock < quantity:
                return Response(
                    {'error': 'Insufficient stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item.quantity = quantity
            cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, item_id):
        """Remove item from cart"""
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Create order from cart"""
        with transaction.atomic():
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                return Response(
                    {'error': 'Cart is empty'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not cart.items.exists():
                return Response(
                    {'error': 'Cart is empty'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate totals
            subtotal = 0
            items_data = []
            
            for cart_item in cart.items.all():
                product = cart_item.product
                unit_price = product.discounted_price or product.price
                total_price = cart_item.quantity * unit_price
                subtotal += total_price
                
                # Check inventory
                if hasattr(product, 'inventory') and product.inventory.stock < cart_item.quantity:
                    return Response(
                        {'error': f'Insufficient stock for {product.title}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                items_data.append({
                    'product_id': product.id,
                    'quantity': cart_item.quantity
                })
            
            # Create order data
            order_data = {
                'subtotal': subtotal,
                'tax_amount': subtotal * 0.1,  # 10% tax
                'shipping_cost': 10.0,  # Fixed shipping cost
                'discount_amount': 0,
                'shipping_address': request.data.get('shipping_address'),
                'billing_address': request.data.get('billing_address'),
                'notes': request.data.get('notes', ''),
                'items': items_data
            }
            
            serializer = self.get_serializer(data=order_data)
            if serializer.is_valid():
                order = serializer.save()
                
                # Update inventory
                for cart_item in cart.items.all():
                    if hasattr(cart_item.product, 'inventory'):
                        cart_item.product.inventory.stock -= cart_item.quantity
                        cart_item.product.inventory.save()
                
                # Clear cart
                cart.items.all().delete()
                
                logger.info(f"Order {order.order_number} created for user {request.user.phone}")
                
                return Response(
                    OrderSerializer(order).data, 
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, order_id):
        """Update order status (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if new_status not in [choice[0] for choice in Order.ORDER_STATUS_CHOICES]:
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = order.status
        order.status = new_status
        
        # Update timestamps based on status
        if new_status == 'SHIPPED' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'DELIVERED' and not order.delivered_at:
            order.delivered_at = timezone.now()
        
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
            notes=notes or f"Status changed from {old_status} to {new_status}",
            created_by=request.user
        )
        
        logger.info(f"Order {order.order_number} status changed from {old_status} to {new_status}")
        
        return Response(OrderSerializer(order).data)


class PaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_id):
        """Create payment for order"""
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        if order.payment_status == 'PAID':
            return Response(
                {'error': 'Order already paid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment_data = serializer.validated_data
            payment_data['order'] = order
            payment_data['transaction_id'] = f"TXN-{uuid.uuid4().hex[:16].upper()}"
            payment_data['amount'] = order.total_amount
            
            payment = Payment.objects.create(**payment_data)
            
            # In a real application, you would integrate with payment gateway here
            # For demo purposes, we'll simulate successful payment
            payment.status = 'COMPLETED'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update order payment status
            order.payment_status = 'PAID'
            order.status = 'CONFIRMED'
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status='CONFIRMED',
                notes='Payment completed',
                created_by=request.user
            )
            
            logger.info(f"Payment {payment.transaction_id} completed for order {order.order_number}")
            
            return Response(
                PaymentSerializer(payment).data, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get order analytics for user"""
        user_orders = Order.objects.filter(user=request.user)
        
        analytics = {
            'total_orders': user_orders.count(),
            'total_spent': sum(order.total_amount for order in user_orders if order.payment_status == 'PAID'),
            'pending_orders': user_orders.filter(status='PENDING').count(),
            'delivered_orders': user_orders.filter(status='DELIVERED').count(),
            'average_order_value': 0,
        }
        
        paid_orders = user_orders.filter(payment_status='PAID')
        if paid_orders.exists():
            analytics['average_order_value'] = sum(order.total_amount for order in paid_orders) / paid_orders.count()
        
        return Response(analytics)
