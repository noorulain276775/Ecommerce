"""
Order Views Tests

This module contains comprehensive tests for order-related API views
including order creation, retrieval, status updates, and payment processing.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

from orders.models import Order, OrderItem, Payment, OrderStatusHistory, Cart, CartItem
from products.models import Product, Category, Seller
from accounts.models import CustomUser

User = get_user_model()


class OrderListCreateViewTestCase(APITestCase):
    """Test cases for OrderListCreateView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.seller = Seller.objects.create(
            name='Test Seller',
            email='seller@test.com',
            phone='1234567890',
            address='Test Address'
        )
        
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic products'
        )
        
        self.product1 = Product.objects.create(
            title='Product 1',
            description='Description 1',
            price=99.99,
            category=self.category,
            seller=self.seller,
            stock=100
        )
        
        self.product2 = Product.objects.create(
            title='Product 2',
            description='Description 2',
            price=149.99,
            category=self.category,
            seller=self.seller,
            stock=50
        )
        
        self.shipping_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'Test Country'
        }
        
        self.orders_url = '/api/orders/'
    
    def test_get_orders_authenticated(self):
        """Test getting orders when authenticated"""
        # Create an order
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.orders_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['order_number'], order.order_number)
    
    def test_get_orders_unauthenticated(self):
        """Test getting orders when not authenticated"""
        response = self.client.get(self.orders_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_orders_user_isolation(self):
        """Test that users can only see their own orders"""
        # Create another user and order
        other_user = CustomUser.objects.create_user(
            phone='9876543210',
            password='testpass123',
            first_name='Other',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        Order.objects.create(
            user=other_user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        # Create order for current user
        user_order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.orders_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['order_number'], user_order.order_number)
    
    def test_create_order_from_cart(self):
        """Test creating order from cart"""
        # Create cart and add items
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)
        CartItem.objects.create(cart=cart, product=self.product2, quantity=1)
        
        self.client.force_authenticate(user=self.user)
        
        order_data = {
            'shipping_address': self.shipping_address,
            'billing_address': self.shipping_address,
            'notes': 'Test order'
        }
        
        response = self.client.post(self.orders_url, order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_number', response.data)
        self.assertEqual(response.data['status'], 'PENDING')
        self.assertEqual(response.data['payment_status'], 'PENDING')
        
        # Verify order was created
        order = Order.objects.get(order_number=response.data['order_number'])
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.items.count(), 2)
        
        # Verify cart was cleared
        self.assertEqual(cart.items.count(), 0)
    
    def test_create_order_empty_cart(self):
        """Test creating order with empty cart"""
        self.client.force_authenticate(user=self.user)
        
        order_data = {
            'shipping_address': self.shipping_address
        }
        
        response = self.client.post(self.orders_url, order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_order_insufficient_stock(self):
        """Test creating order with insufficient stock"""
        # Create cart with quantity exceeding stock
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=150)  # More than stock (100)
        
        self.client.force_authenticate(user=self.user)
        
        order_data = {
            'shipping_address': self.shipping_address
        }
        
        response = self.client.post(self.orders_url, order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_order_missing_shipping_address(self):
        """Test creating order without shipping address"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=1)
        
        self.client.force_authenticate(user=self.user)
        
        order_data = {}  # Missing shipping address
        
        response = self.client.post(self.orders_url, order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_order_invalid_shipping_address(self):
        """Test creating order with invalid shipping address"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=1)
        
        self.client.force_authenticate(user=self.user)
        
        order_data = {
            'shipping_address': {
                'street': '123 Main St',
                'city': 'Test City',
                # Missing required fields
            }
        }
        
        response = self.client.post(self.orders_url, order_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class OrderDetailViewTestCase(APITestCase):
    """Test cases for OrderDetailView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.other_user = CustomUser.objects.create_user(
            phone='9876543210',
            password='testpass123',
            first_name='Other',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.shipping_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'Test Country'
        }
        
        self.order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        self.order_detail_url = f'/api/orders/{self.order.id}/'
    
    def test_get_order_detail_authenticated(self):
        """Test getting order detail when authenticated"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.order_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_number'], self.order.order_number)
        self.assertEqual(response.data['user']['phone'], self.user.phone)
    
    def test_get_order_detail_unauthenticated(self):
        """Test getting order detail when not authenticated"""
        response = self.client.get(self.order_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_order_detail_other_user(self):
        """Test getting order detail for another user's order"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.order_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_nonexistent_order(self):
        """Test getting non-existent order"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/99999999-9999-9999-9999-999999999999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderStatusUpdateViewTestCase(APITestCase):
    """Test cases for OrderStatusUpdateView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.admin_user = CustomUser.objects.create_user(
            phone='9876543210',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            user_type='ADMIN',
            is_staff=True
        )
        
        self.shipping_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'Test Country'
        }
        
        self.order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        self.status_update_url = f'/api/orders/{self.order.id}/status/'
    
    def test_update_order_status_admin(self):
        """Test updating order status as admin"""
        self.client.force_authenticate(user=self.admin_user)
        
        status_data = {
            'status': 'CONFIRMED',
            'notes': 'Order confirmed by admin'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'CONFIRMED')
        
        # Verify order was updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'CONFIRMED')
        
        # Verify status history was created
        self.assertEqual(self.order.status_history.count(), 1)
        history_entry = self.order.status_history.first()
        self.assertEqual(history_entry.status, 'CONFIRMED')
        self.assertEqual(history_entry.created_by, self.admin_user)
    
    def test_update_order_status_non_admin(self):
        """Test updating order status as non-admin"""
        self.client.force_authenticate(user=self.user)
        
        status_data = {
            'status': 'CONFIRMED',
            'notes': 'Order confirmed'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_order_status_unauthenticated(self):
        """Test updating order status when not authenticated"""
        status_data = {
            'status': 'CONFIRMED',
            'notes': 'Order confirmed'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_order_status_invalid_status(self):
        """Test updating order status with invalid status"""
        self.client.force_authenticate(user=self.admin_user)
        
        status_data = {
            'status': 'INVALID_STATUS',
            'notes': 'Invalid status'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_update_order_status_shipped_timestamp(self):
        """Test that shipped_at timestamp is set when status is SHIPPED"""
        self.client.force_authenticate(user=self.admin_user)
        
        status_data = {
            'status': 'SHIPPED',
            'notes': 'Order shipped',
            'tracking_number': 'TRK123456789'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify shipped_at timestamp was set
        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.shipped_at)
    
    def test_update_order_status_delivered_timestamp(self):
        """Test that delivered_at timestamp is set when status is DELIVERED"""
        self.client.force_authenticate(user=self.admin_user)
        
        status_data = {
            'status': 'DELIVERED',
            'notes': 'Order delivered'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify delivered_at timestamp was set
        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.delivered_at)


class PaymentViewTestCase(APITestCase):
    """Test cases for PaymentView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.shipping_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'Test Country'
        }
        
        self.order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        self.payment_url = f'/api/orders/{self.order.id}/payment/'
    
    def test_create_payment_success(self):
        """Test successful payment creation"""
        self.client.force_authenticate(user=self.user)
        
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('119.98')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('transaction_id', response.data)
        self.assertEqual(response.data['payment_method'], 'CARD')
        self.assertEqual(response.data['status'], 'COMPLETED')
        
        # Verify payment was created
        payment = Payment.objects.get(transaction_id=response.data['transaction_id'])
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.amount, Decimal('119.98'))
        self.assertEqual(payment.status, 'COMPLETED')
        
        # Verify order was updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'PAID')
        self.assertEqual(self.order.status, 'CONFIRMED')
    
    def test_create_payment_unauthenticated(self):
        """Test creating payment when not authenticated"""
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('119.98')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_payment_other_user_order(self):
        """Test creating payment for another user's order"""
        other_user = CustomUser.objects.create_user(
            phone='9876543210',
            password='testpass123',
            first_name='Other',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.client.force_authenticate(user=other_user)
        
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('119.98')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_payment_already_paid(self):
        """Test creating payment for already paid order"""
        # Create payment for order
        Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='COMPLETED'
        )
        
        self.order.payment_status = 'PAID'
        self.order.save()
        
        self.client.force_authenticate(user=self.user)
        
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('119.98')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_payment_invalid_data(self):
        """Test creating payment with invalid data"""
        self.client.force_authenticate(user=self.user)
        
        payment_data = {
            'payment_method': 'INVALID_METHOD',
            'amount': Decimal('-10.00')  # Negative amount
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_payment_wrong_amount(self):
        """Test creating payment with wrong amount"""
        self.client.force_authenticate(user=self.user)
        
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('50.00')  # Wrong amount
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        # The view should still create payment with correct amount
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '119.98')  # Correct amount


class OrderAnalyticsViewTestCase(APITestCase):
    """Test cases for OrderAnalyticsView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.shipping_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'Test Country'
        }
        
        self.analytics_url = '/api/orders/analytics/'
    
    def test_get_analytics_authenticated(self):
        """Test getting analytics when authenticated"""
        # Create orders with different statuses
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address,
            status='PENDING',
            payment_status='PENDING'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('199.99'),
            total_amount=Decimal('219.99'),
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.analytics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 3)
        self.assertEqual(response.data['pending_orders'], 1)
        self.assertEqual(response.data['delivered_orders'], 2)
        self.assertEqual(response.data['total_spent'], Decimal('389.98'))  # 169.99 + 219.99
        self.assertEqual(response.data['average_order_value'], Decimal('194.99'))  # 389.98 / 2
    
    def test_get_analytics_unauthenticated(self):
        """Test getting analytics when not authenticated"""
        response = self.client.get(self.analytics_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_analytics_no_orders(self):
        """Test getting analytics with no orders"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.analytics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 0)
        self.assertEqual(response.data['total_spent'], 0)
        self.assertEqual(response.data['average_order_value'], 0)
    
    def test_get_analytics_user_isolation(self):
        """Test that analytics are user-specific"""
        # Create another user with orders
        other_user = CustomUser.objects.create_user(
            phone='9876543210',
            password='testpass123',
            first_name='Other',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        Order.objects.create(
            user=other_user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        # Create order for current user
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.analytics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 1)  # Only current user's orders
        self.assertEqual(response.data['total_spent'], Decimal('169.99'))


class OrderViewIntegrationTestCase(APITestCase):
    """Integration test cases for order views"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.admin_user = CustomUser.objects.create_user(
            phone='9876543210',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            user_type='ADMIN',
            is_staff=True
        )
        
        self.seller = Seller.objects.create(
            name='Test Seller',
            email='seller@test.com',
            phone='1234567890',
            address='Test Address'
        )
        
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic products'
        )
        
        self.product = Product.objects.create(
            title='Test Product',
            description='Test Description',
            price=99.99,
            category=self.category,
            seller=self.seller,
            stock=100
        )
        
        self.shipping_address = {
            'street': '123 Main St',
            'city': 'Test City',
            'state': 'Test State',
            'postal_code': '12345',
            'country': 'Test Country'
        }
    
    def test_complete_order_workflow(self):
        """Test complete order workflow from cart to delivery"""
        # Step 1: Add items to cart
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        self.client.force_authenticate(user=self.user)
        
        # Step 2: Create order from cart
        order_data = {
            'shipping_address': self.shipping_address,
            'notes': 'Test order workflow'
        }
        
        order_response = self.client.post('/api/orders/', order_data, format='json')
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        
        order_id = order_response.data['id']
        
        # Step 3: Create payment
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('219.98')
        }
        
        payment_response = self.client.post(f'/api/orders/{order_id}/payment/', payment_data, format='json')
        self.assertEqual(payment_response.status_code, status.HTTP_201_CREATED)
        
        # Step 4: Update order status (admin)
        self.client.force_authenticate(user=self.admin_user)
        
        status_data = {
            'status': 'PROCESSING',
            'notes': 'Order is being processed'
        }
        
        status_response = self.client.patch(f'/api/orders/{order_id}/status/', status_data, format='json')
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        
        # Step 5: Ship order
        status_data = {
            'status': 'SHIPPED',
            'notes': 'Order has been shipped',
            'tracking_number': 'TRK123456789'
        }
        
        status_response = self.client.patch(f'/api/orders/{order_id}/status/', status_data, format='json')
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        
        # Step 6: Deliver order
        status_data = {
            'status': 'DELIVERED',
            'notes': 'Order has been delivered'
        }
        
        status_response = self.client.patch(f'/api/orders/{order_id}/status/', status_data, format='json')
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        
        # Verify final order state
        self.client.force_authenticate(user=self.user)
        order_detail_response = self.client.get(f'/api/orders/{order_id}/')
        self.assertEqual(order_detail_response.status_code, status.HTTP_200_OK)
        
        order_data = order_detail_response.data
        self.assertEqual(order_data['status'], 'DELIVERED')
        self.assertEqual(order_data['payment_status'], 'PAID')
        self.assertEqual(len(order_data['status_history']), 4)  # PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED
        
        # Verify analytics
        analytics_response = self.client.get('/api/orders/analytics/')
        self.assertEqual(analytics_response.status_code, status.HTTP_200_OK)
        self.assertEqual(analytics_response.data['total_orders'], 1)
        self.assertEqual(analytics_response.data['delivered_orders'], 1)
        self.assertEqual(analytics_response.data['total_spent'], Decimal('219.98'))
    
    def test_order_cancellation_workflow(self):
        """Test order cancellation workflow"""
        # Create order
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        # Create payment
        self.client.force_authenticate(user=self.user)
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('119.98')
        }
        
        payment_response = self.client.post(f'/api/orders/{order.id}/payment/', payment_data, format='json')
        self.assertEqual(payment_response.status_code, status.HTTP_201_CREATED)
        
        # Cancel order (admin)
        self.client.force_authenticate(user=self.admin_user)
        status_data = {
            'status': 'CANCELLED',
            'notes': 'Order cancelled by customer request'
        }
        
        status_response = self.client.patch(f'/api/orders/{order.id}/status/', status_data, format='json')
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        
        # Verify order is cancelled
        order.refresh_from_db()
        self.assertEqual(order.status, 'CANCELLED')
        
        # Verify status history
        self.assertEqual(order.status_history.count(), 2)  # PENDING, CONFIRMED, CANCELLED
