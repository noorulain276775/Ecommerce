"""
Order Models Tests

This module contains comprehensive tests for order-related models
including Order, OrderItem, Payment, and OrderStatusHistory.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid

from orders.models import Order, OrderItem, Payment, OrderStatusHistory
from products.models import Product, Category, Seller
from accounts.models import CustomUser

User = get_user_model()


class OrderModelTestCase(TestCase):
    """Test cases for Order model"""
    
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
        
        self.order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            tax_amount=Decimal('9.99'),
            shipping_cost=Decimal('10.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
    
    def test_order_creation(self):
        """Test order creation"""
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.subtotal, Decimal('99.99'))
        self.assertEqual(self.order.tax_amount, Decimal('9.99'))
        self.assertEqual(self.order.shipping_cost, Decimal('10.00'))
        self.assertEqual(self.order.total_amount, Decimal('119.98'))
        self.assertEqual(self.order.status, 'PENDING')
        self.assertEqual(self.order.payment_status, 'PENDING')
        self.assertIsNotNone(self.order.order_number)
    
    def test_order_number_generation(self):
        """Test automatic order number generation"""
        self.assertTrue(self.order.order_number.startswith('ORD-'))
        self.assertIn(str(self.order.id)[:8].upper(), self.order.order_number)
    
    def test_order_str_representation(self):
        """Test order string representation"""
        expected_str = f"Order {self.order.order_number} - {self.user.phone}"
        self.assertEqual(str(self.order), expected_str)
    
    def test_order_calculate_total(self):
        """Test order total calculation"""
        calculated_total = self.order.calculate_total()
        expected_total = Decimal('119.98')  # 99.99 + 9.99 + 10.00 - 0.00
        self.assertEqual(calculated_total, expected_total)
    
    def test_order_status_choices(self):
        """Test order status choices"""
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        self.assertIn('PENDING', valid_statuses)
        self.assertIn('CONFIRMED', valid_statuses)
        self.assertIn('PROCESSING', valid_statuses)
        self.assertIn('SHIPPED', valid_statuses)
        self.assertIn('DELIVERED', valid_statuses)
        self.assertIn('CANCELLED', valid_statuses)
        self.assertIn('REFUNDED', valid_statuses)
    
    def test_payment_status_choices(self):
        """Test payment status choices"""
        valid_statuses = [choice[0] for choice in Order.PAYMENT_STATUS_CHOICES]
        self.assertIn('PENDING', valid_statuses)
        self.assertIn('PAID', valid_statuses)
        self.assertIn('FAILED', valid_statuses)
        self.assertIn('REFUNDED', valid_statuses)
    
    def test_order_negative_amounts_validation(self):
        """Test validation of negative amounts"""
        with self.assertRaises(ValidationError):
            order = Order(
                user=self.user,
                subtotal=Decimal('-10.00'),  # Negative subtotal
                total_amount=Decimal('100.00'),
                shipping_address=self.shipping_address
            )
            order.full_clean()
    
    def test_order_required_fields(self):
        """Test required fields validation"""
        with self.assertRaises(ValidationError):
            order = Order()  # Missing required fields
            order.full_clean()
    
    def test_order_meta_ordering(self):
        """Test order meta ordering"""
        # Create another order
        Order.objects.create(
            user=self.user,
            subtotal=Decimal('50.00'),
            total_amount=Decimal('60.00'),
            shipping_address=self.shipping_address
        )
        
        orders = Order.objects.all()
        self.assertEqual(orders[0], self.order)  # Most recent first


class OrderItemModelTestCase(TestCase):
    """Test cases for OrderItem model"""
    
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
        
        self.order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('199.98'),
            total_amount=Decimal('219.98'),
            shipping_address=self.shipping_address
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('99.99')
        )
    
    def test_order_item_creation(self):
        """Test order item creation"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.unit_price, Decimal('99.99'))
        self.assertEqual(self.order_item.total_price, Decimal('199.98'))
    
    def test_order_item_str_representation(self):
        """Test order item string representation"""
        expected_str = f"{self.product.title} x {self.order_item.quantity}"
        self.assertEqual(str(self.order_item), expected_str)
    
    def test_order_item_total_price_calculation(self):
        """Test order item total price calculation"""
        expected_total = Decimal('199.98')  # 99.99 * 2
        self.assertEqual(self.order_item.total_price, expected_total)
    
    def test_order_item_product_snapshot(self):
        """Test order item product snapshot creation"""
        self.assertIsNotNone(self.order_item.product_snapshot)
        self.assertEqual(self.order_item.product_snapshot['title'], self.product.title)
        self.assertEqual(self.order_item.product_snapshot['description'], self.product.description)
        self.assertEqual(self.order_item.product_snapshot['category'], self.product.category.name)
        self.assertEqual(self.order_item.product_snapshot['seller'], self.product.seller.name)
    
    def test_order_item_quantity_validation(self):
        """Test order item quantity validation"""
        with self.assertRaises(ValidationError):
            order_item = OrderItem(
                order=self.order,
                product=self.product,
                quantity=0,  # Invalid quantity
                unit_price=Decimal('99.99')
            )
            order_item.full_clean()
    
    def test_order_item_unit_price_validation(self):
        """Test order item unit price validation"""
        with self.assertRaises(ValidationError):
            order_item = OrderItem(
                order=self.order,
                product=self.product,
                quantity=1,
                unit_price=Decimal('-10.00')  # Negative price
            )
            order_item.full_clean()
    
    def test_order_item_unique_together(self):
        """Test order item unique together constraint"""
        # Try to create another order item with same order and product
        with self.assertRaises(Exception):  # IntegrityError
            OrderItem.objects.create(
                order=self.order,
                product=self.product,
                quantity=1,
                unit_price=Decimal('99.99')
            )


class PaymentModelTestCase(TestCase):
    """Test cases for Payment model"""
    
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
        
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PENDING'
        )
    
    def test_payment_creation(self):
        """Test payment creation"""
        self.assertEqual(self.payment.order, self.order)
        self.assertEqual(self.payment.payment_method, 'CARD')
        self.assertEqual(self.payment.transaction_id, 'TXN-1234567890')
        self.assertEqual(self.payment.amount, Decimal('119.98'))
        self.assertEqual(self.payment.status, 'PENDING')
    
    def test_payment_str_representation(self):
        """Test payment string representation"""
        expected_str = f"Payment {self.payment.transaction_id} - {self.payment.amount}"
        self.assertEqual(str(self.payment), expected_str)
    
    def test_payment_method_choices(self):
        """Test payment method choices"""
        valid_methods = [choice[0] for choice in Payment.PAYMENT_METHOD_CHOICES]
        self.assertIn('CARD', valid_methods)
        self.assertIn('PAYPAL', valid_methods)
        self.assertIn('BANK_TRANSFER', valid_methods)
        self.assertIn('COD', valid_methods)
    
    def test_payment_status_choices(self):
        """Test payment status choices"""
        valid_statuses = [choice[0] for choice in Payment.PAYMENT_STATUS_CHOICES]
        self.assertIn('PENDING', valid_statuses)
        self.assertIn('PROCESSING', valid_statuses)
        self.assertIn('COMPLETED', valid_statuses)
        self.assertIn('FAILED', valid_statuses)
        self.assertIn('CANCELLED', valid_statuses)
        self.assertIn('REFUNDED', valid_statuses)
    
    def test_payment_amount_validation(self):
        """Test payment amount validation"""
        with self.assertRaises(ValidationError):
            payment = Payment(
                order=self.order,
                payment_method='CARD',
                transaction_id='TXN-1234567891',
                amount=Decimal('-10.00'),  # Negative amount
                status='PENDING'
            )
            payment.full_clean()
    
    def test_payment_unique_transaction_id(self):
        """Test payment unique transaction ID constraint"""
        with self.assertRaises(Exception):  # IntegrityError
            Payment.objects.create(
                order=self.order,
                payment_method='CARD',
                transaction_id='TXN-1234567890',  # Same transaction ID
                amount=Decimal('119.98'),
                status='PENDING'
            )
    
    def test_payment_one_to_one_with_order(self):
        """Test payment one-to-one relationship with order"""
        # Try to create another payment for the same order
        with self.assertRaises(Exception):  # IntegrityError
            Payment.objects.create(
                order=self.order,
                payment_method='PAYPAL',
                transaction_id='TXN-1234567892',
                amount=Decimal('119.98'),
                status='PENDING'
            )


class OrderStatusHistoryModelTestCase(TestCase):
    """Test cases for OrderStatusHistory model"""
    
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
        
        self.status_history = OrderStatusHistory.objects.create(
            order=self.order,
            status='PENDING',
            notes='Order created',
            created_by=self.user
        )
    
    def test_status_history_creation(self):
        """Test status history creation"""
        self.assertEqual(self.status_history.order, self.order)
        self.assertEqual(self.status_history.status, 'PENDING')
        self.assertEqual(self.status_history.notes, 'Order created')
        self.assertEqual(self.status_history.created_by, self.user)
        self.assertIsNotNone(self.status_history.created_at)
    
    def test_status_history_str_representation(self):
        """Test status history string representation"""
        expected_str = f"{self.order.order_number} - PENDING"
        self.assertEqual(str(self.status_history), expected_str)
    
    def test_status_history_ordering(self):
        """Test status history ordering"""
        # Create another status history entry
        OrderStatusHistory.objects.create(
            order=self.order,
            status='CONFIRMED',
            notes='Order confirmed',
            created_by=self.admin_user
        )
        
        history_entries = OrderStatusHistory.objects.filter(order=self.order)
        self.assertEqual(history_entries[0].status, 'CONFIRMED')  # Most recent first
        self.assertEqual(history_entries[1].status, 'PENDING')
    
    def test_status_history_without_created_by(self):
        """Test status history creation without created_by"""
        status_history = OrderStatusHistory.objects.create(
            order=self.order,
            status='SHIPPED',
            notes='Order shipped'
        )
        
        self.assertIsNone(status_history.created_by)
        self.assertEqual(status_history.status, 'SHIPPED')


class OrderModelIntegrationTestCase(TestCase):
    """Integration test cases for order models"""
    
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
    
    def test_complete_order_workflow(self):
        """Test complete order workflow"""
        # Create order
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('249.98'),
            tax_amount=Decimal('24.99'),
            shipping_cost=Decimal('10.00'),
            discount_amount=Decimal('0.00'),
            total_amount=Decimal('284.97'),
            shipping_address=self.shipping_address
        )
        
        # Create order items
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=1,
            unit_price=Decimal('99.99')
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product2,
            quantity=1,
            unit_price=Decimal('149.99')
        )
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='PENDING',
            notes='Order created',
            created_by=self.user
        )
        
        # Create payment
        payment = Payment.objects.create(
            order=order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('284.97'),
            status='COMPLETED'
        )
        
        # Update order status
        order.payment_status = 'PAID'
        order.status = 'CONFIRMED'
        order.save()
        
        # Create status history for confirmation
        OrderStatusHistory.objects.create(
            order=order,
            status='CONFIRMED',
            notes='Payment completed',
            created_by=self.user
        )
        
        # Verify order
        self.assertEqual(order.status, 'CONFIRMED')
        self.assertEqual(order.payment_status, 'PAID')
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.status_history.count(), 2)
        self.assertEqual(order.payment, payment)
        
        # Verify order items
        total_items = sum(item.quantity for item in order.items.all())
        self.assertEqual(total_items, 2)
        
        # Verify payment
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(payment.amount, order.total_amount)
    
    def test_order_with_discount(self):
        """Test order with discount"""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            tax_amount=Decimal('9.99'),
            shipping_cost=Decimal('10.00'),
            discount_amount=Decimal('20.00'),
            total_amount=Decimal('99.98'),
            shipping_address=self.shipping_address
        )
        
        calculated_total = order.calculate_total()
        expected_total = Decimal('99.98')  # 99.99 + 9.99 + 10.00 - 20.00
        self.assertEqual(calculated_total, expected_total)
    
    def test_order_status_transitions(self):
        """Test order status transitions"""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        # Test status transitions
        statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        
        for i, status in enumerate(statuses):
            order.status = status
            order.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status=status,
                notes=f'Status changed to {status}',
                created_by=self.user
            )
            
            self.assertEqual(order.status, status)
        
        # Verify all status history entries
        self.assertEqual(order.status_history.count(), len(statuses))
        
        # Verify ordering (most recent first)
        history_entries = order.status_history.all()
        for i, entry in enumerate(history_entries):
            self.assertEqual(entry.status, statuses[-(i+1)])
    
    def test_order_cancellation_workflow(self):
        """Test order cancellation workflow"""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal('99.99'),
            total_amount=Decimal('119.98'),
            shipping_address=self.shipping_address
        )
        
        # Create payment
        payment = Payment.objects.create(
            order=order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='COMPLETED'
        )
        
        # Cancel order
        order.status = 'CANCELLED'
        order.save()
        
        # Refund payment
        payment.status = 'REFUNDED'
        payment.save()
        
        order.payment_status = 'REFUNDED'
        order.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='CANCELLED',
            notes='Order cancelled and refunded',
            created_by=self.user
        )
        
        # Verify cancellation
        self.assertEqual(order.status, 'CANCELLED')
        self.assertEqual(order.payment_status, 'REFUNDED')
        self.assertEqual(payment.status, 'REFUNDED')
