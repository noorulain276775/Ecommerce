"""
Order Analytics Tests

This module contains comprehensive tests for order analytics,
reporting, and business intelligence features.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import datetime, timedelta
import json

from orders.models import Order, OrderItem, Payment, OrderStatusHistory
from products.models import Product, Category, Seller
from accounts.models import CustomUser

User = get_user_model()


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
        self.assertEqual(response.data['pending_orders'], 0)
        self.assertEqual(response.data['delivered_orders'], 0)
    
    def test_get_analytics_user_isolation(self):
        """Test that analytics are user-specific"""
        # Create orders for other user
        Order.objects.create(
            user=self.other_user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        Order.objects.create(
            user=self.other_user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        # Create order for current user
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
        self.assertEqual(response.data['total_orders'], 1)  # Only current user's orders
        self.assertEqual(response.data['total_spent'], Decimal('219.99'))
        self.assertEqual(response.data['average_order_value'], Decimal('219.99'))
    
    def test_get_analytics_with_different_statuses(self):
        """Test analytics with different order statuses"""
        # Create orders with various statuses
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
            status='CONFIRMED',
            payment_status='PAID'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('199.99'),
            total_amount=Decimal('219.99'),
            shipping_address=self.shipping_address,
            status='PROCESSING',
            payment_status='PAID'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('249.99'),
            total_amount=Decimal('269.99'),
            shipping_address=self.shipping_address,
            status='SHIPPED',
            payment_status='PAID'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('299.99'),
            total_amount=Decimal('319.99'),
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('349.99'),
            total_amount=Decimal('369.99'),
            shipping_address=self.shipping_address,
            status='CANCELLED',
            payment_status='REFUNDED'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.analytics_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_orders'], 6)
        self.assertEqual(response.data['pending_orders'], 1)
        self.assertEqual(response.data['delivered_orders'], 1)
        # Only paid orders count towards total_spent
        self.assertEqual(response.data['total_spent'], Decimal('759.97'))  # 169.99 + 219.99 + 269.99 + 319.99
        self.assertEqual(response.data['average_order_value'], Decimal('189.99'))  # 759.97 / 4
    
    def test_get_analytics_with_failed_payments(self):
        """Test analytics with failed payments"""
        # Create order with failed payment
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address,
            status='PENDING',
            payment_status='FAILED'
        )
        
        # Create order with successful payment
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
        self.assertEqual(response.data['total_orders'], 2)
        self.assertEqual(response.data['total_spent'], Decimal('169.99'))  # Only paid order
        self.assertEqual(response.data['average_order_value'], Decimal('169.99'))


class OrderAnalyticsModelTestCase(TestCase):
    """Test cases for order analytics model methods"""
    
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
    
    def test_order_total_calculation(self):
        """Test order total calculation"""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('249.98'),
            tax_amount=Decimal('24.99'),
            shipping_cost=Decimal('10.00'),
            discount_amount=Decimal('20.00'),
            total_amount=Decimal('264.97'),
            shipping_address=self.shipping_address
        )
        
        calculated_total = order.calculate_total()
        expected_total = Decimal('264.97')  # 249.98 + 24.99 + 10.00 - 20.00
        self.assertEqual(calculated_total, expected_total)
    
    def test_order_items_count(self):
        """Test order items count calculation"""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('249.98'),
            total_amount=Decimal('264.97'),
            shipping_address=self.shipping_address
        )
        
        # Add order items
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            unit_price=Decimal('99.99')
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product2,
            quantity=1,
            unit_price=Decimal('149.99')
        )
        
        # Calculate total items
        total_items = sum(item.quantity for item in order.items.all())
        self.assertEqual(total_items, 3)  # 2 + 1
    
    def test_order_status_distribution(self):
        """Test order status distribution"""
        # Create orders with different statuses
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address,
            status='PENDING'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address,
            status='CONFIRMED'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('199.99'),
            total_amount=Decimal('219.99'),
            shipping_address=self.shipping_address,
            status='DELIVERED'
        )
        
        # Get status distribution
        user_orders = Order.objects.filter(user=self.user)
        status_distribution = {}
        
        for order in user_orders:
            status_distribution[order.status] = status_distribution.get(order.status, 0) + 1
        
        self.assertEqual(status_distribution['PENDING'], 1)
        self.assertEqual(status_distribution['CONFIRMED'], 1)
        self.assertEqual(status_distribution['DELIVERED'], 1)
    
    def test_order_payment_status_distribution(self):
        """Test order payment status distribution"""
        # Create orders with different payment statuses
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address,
            payment_status='PENDING'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address,
            payment_status='PAID'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('199.99'),
            total_amount=Decimal('219.99'),
            shipping_address=self.shipping_address,
            payment_status='FAILED'
        )
        
        # Get payment status distribution
        user_orders = Order.objects.filter(user=self.user)
        payment_status_distribution = {}
        
        for order in user_orders:
            payment_status_distribution[order.payment_status] = payment_status_distribution.get(order.payment_status, 0) + 1
        
        self.assertEqual(payment_status_distribution['PENDING'], 1)
        self.assertEqual(payment_status_distribution['PAID'], 1)
        self.assertEqual(payment_status_distribution['FAILED'], 1)


class OrderAnalyticsTimeBasedTestCase(TestCase):
    """Test cases for time-based order analytics"""
    
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
    
    def test_orders_by_date_range(self):
        """Test orders filtered by date range"""
        # Create orders on different dates
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        
        # Order from yesterday
        order1 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        order1.created_at = yesterday
        order1.save()
        
        # Order from last week
        order2 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address
        )
        order2.created_at = last_week
        order2.save()
        
        # Order from today
        order3 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('199.99'),
            total_amount=Decimal('219.99'),
            shipping_address=self.shipping_address
        )
        
        # Filter orders from last 3 days
        three_days_ago = today - timedelta(days=3)
        recent_orders = Order.objects.filter(
            user=self.user,
            created_at__gte=three_days_ago
        )
        
        self.assertEqual(recent_orders.count(), 2)  # Today and yesterday
        
        # Filter orders from last week
        week_ago = today - timedelta(days=7)
        week_orders = Order.objects.filter(
            user=self.user,
            created_at__gte=week_ago
        )
        
        self.assertEqual(week_orders.count(), 3)  # All orders
    
    def test_monthly_order_analytics(self):
        """Test monthly order analytics"""
        # Create orders in different months
        current_month = timezone.now().replace(day=1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        # Order from current month
        order1 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        order1.created_at = current_month + timedelta(days=5)
        order1.save()
        
        # Order from last month
        order2 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address
        )
        order2.created_at = last_month + timedelta(days=10)
        order2.save()
        
        # Get current month orders
        current_month_orders = Order.objects.filter(
            user=self.user,
            created_at__year=current_month.year,
            created_at__month=current_month.month
        )
        
        self.assertEqual(current_month_orders.count(), 1)
        
        # Get last month orders
        last_month_orders = Order.objects.filter(
            user=self.user,
            created_at__year=last_month.year,
            created_at__month=last_month.month
        )
        
        self.assertEqual(last_month_orders.count(), 1)
    
    def test_yearly_order_analytics(self):
        """Test yearly order analytics"""
        # Create orders in different years
        current_year = timezone.now().year
        last_year = current_year - 1
        
        # Order from current year
        order1 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        order1.created_at = timezone.datetime(current_year, 6, 15, tzinfo=timezone.utc)
        order1.save()
        
        # Order from last year
        order2 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address
        )
        order2.created_at = timezone.datetime(last_year, 12, 20, tzinfo=timezone.utc)
        order2.save()
        
        # Get current year orders
        current_year_orders = Order.objects.filter(
            user=self.user,
            created_at__year=current_year
        )
        
        self.assertEqual(current_year_orders.count(), 1)
        
        # Get last year orders
        last_year_orders = Order.objects.filter(
            user=self.user,
            created_at__year=last_year
        )
        
        self.assertEqual(last_year_orders.count(), 1)


class OrderAnalyticsBusinessIntelligenceTestCase(TestCase):
    """Test cases for business intelligence features"""
    
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
        
        self.category1 = Category.objects.create(
            name='Electronics',
            description='Electronic products'
        )
        
        self.category2 = Category.objects.create(
            name='Books',
            description='Book products'
        )
        
        self.product1 = Product.objects.create(
            title='Electronics Product',
            description='Electronics Description',
            price=99.99,
            category=self.category1,
            seller=self.seller,
            stock=100
        )
        
        self.product2 = Product.objects.create(
            title='Book Product',
            description='Book Description',
            price=29.99,
            category=self.category2,
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
    
    def test_category_analytics(self):
        """Test category-based analytics"""
        # Create orders with different categories
        order1 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        OrderItem.objects.create(
            order=order1,
            product=self.product1,
            quantity=1,
            unit_price=Decimal('99.99')
        )
        
        order2 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('29.99'),
            total_amount=Decimal('39.99'),
            shipping_address=self.shipping_address
        )
        
        OrderItem.objects.create(
            order=order2,
            product=self.product2,
            quantity=1,
            unit_price=Decimal('29.99')
        )
        
        # Get category analytics
        category_stats = {}
        
        for order in Order.objects.filter(user=self.user):
            for item in order.items.all():
                category_name = item.product.category.name
                if category_name not in category_stats:
                    category_stats[category_name] = {
                        'orders': 0,
                        'total_amount': Decimal('0.00'),
                        'total_items': 0
                    }
                
                category_stats[category_name]['orders'] += 1
                category_stats[category_name]['total_amount'] += item.total_price
                category_stats[category_name]['total_items'] += item.quantity
        
        self.assertEqual(category_stats['Electronics']['orders'], 1)
        self.assertEqual(category_stats['Electronics']['total_amount'], Decimal('99.99'))
        self.assertEqual(category_stats['Books']['orders'], 1)
        self.assertEqual(category_stats['Books']['total_amount'], Decimal('29.99'))
    
    def test_seller_analytics(self):
        """Test seller-based analytics"""
        # Create orders with different sellers
        order1 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        OrderItem.objects.create(
            order=order1,
            product=self.product1,
            quantity=1,
            unit_price=Decimal('99.99')
        )
        
        order2 = Order.objects.create(
            user=self.user,
            subtotal=Decimal('29.99'),
            total_amount=Decimal('39.99'),
            shipping_address=self.shipping_address
        )
        
        OrderItem.objects.create(
            order=order2,
            product=self.product2,
            quantity=1,
            unit_price=Decimal('29.99')
        )
        
        # Get seller analytics
        seller_stats = {}
        
        for order in Order.objects.filter(user=self.user):
            for item in order.items.all():
                seller_name = item.product.seller.name
                if seller_name not in seller_stats:
                    seller_stats[seller_name] = {
                        'orders': 0,
                        'total_amount': Decimal('0.00'),
                        'total_items': 0
                    }
                
                seller_stats[seller_name]['orders'] += 1
                seller_stats[seller_name]['total_amount'] += item.total_price
                seller_stats[seller_name]['total_items'] += item.quantity
        
        self.assertEqual(seller_stats['Test Seller']['orders'], 2)
        self.assertEqual(seller_stats['Test Seller']['total_amount'], Decimal('129.98'))
        self.assertEqual(seller_stats['Test Seller']['total_items'], 2)
    
    def test_order_frequency_analytics(self):
        """Test order frequency analytics"""
        # Create orders with different frequencies
        base_date = timezone.now()
        
        # Create 3 orders in the last month
        for i in range(3):
            order = Order.objects.create(
                user=self.user,
                subtotal=Decimal('99.99'),
                total_amount=Decimal('119.98'),
                shipping_address=self.shipping_address
            )
            order.created_at = base_date - timedelta(days=i*10)
            order.save()
        
        # Calculate order frequency
        total_orders = Order.objects.filter(user=self.user).count()
        days_since_first_order = (base_date - Order.objects.filter(user=self.user).order_by('created_at').first().created_at).days
        
        if days_since_first_order > 0:
            order_frequency = total_orders / days_since_first_order
        else:
            order_frequency = total_orders
        
        self.assertEqual(total_orders, 3)
        self.assertGreater(order_frequency, 0)
    
    def test_average_order_value_trend(self):
        """Test average order value trend"""
        # Create orders with different values
        order_values = [Decimal('99.99'), Decimal('149.99'), Decimal('199.99'), Decimal('249.99')]
        
        for value in order_values:
            Order.objects.create(
                user=self.user,
                subtotal=value,
                total_amount=value + Decimal('20.00'),
                shipping_address=self.shipping_address,
                payment_status='PAID'
            )
        
        # Calculate average order value
        paid_orders = Order.objects.filter(user=self.user, payment_status='PAID')
        total_spent = sum(order.total_amount for order in paid_orders)
        average_order_value = total_spent / paid_orders.count()
        
        expected_average = sum(order_values) / len(order_values) + Decimal('20.00')
        self.assertEqual(average_order_value, expected_average)
    
    def test_order_completion_rate(self):
        """Test order completion rate"""
        # Create orders with different statuses
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('149.99'),
            total_amount=Decimal('169.99'),
            shipping_address=self.shipping_address,
            status='CANCELLED',
            payment_status='REFUNDED'
        )
        
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('199.99'),
            total_amount=Decimal('219.99'),
            shipping_address=self.shipping_address,
            status='PENDING',
            payment_status='PENDING'
        )
        
        # Calculate completion rate
        total_orders = Order.objects.filter(user=self.user).count()
        completed_orders = Order.objects.filter(
            user=self.user,
            status='DELIVERED',
            payment_status='PAID'
        ).count()
        
        completion_rate = (completed_orders / total_orders) * 100 if total_orders > 0 else 0
        
        self.assertEqual(total_orders, 3)
        self.assertEqual(completed_orders, 1)
        self.assertEqual(completion_rate, 33.33)  # 1/3 * 100
