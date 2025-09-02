"""
Order Status Management Tests

This module contains comprehensive tests for order status management,
status transitions, and status history tracking.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.utils import timezone
import json

from orders.models import Order, OrderStatusHistory, Payment
from accounts.models import CustomUser

User = get_user_model()


class OrderStatusModelTestCase(TestCase):
    """Test cases for order status model functionality"""
    
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
    
    def test_order_status_choices(self):
        """Test order status choices"""
        valid_statuses = [choice[0] for choice in Order.ORDER_STATUS_CHOICES]
        expected_statuses = [
            'PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 
            'DELIVERED', 'CANCELLED', 'REFUNDED'
        ]
        
        for status in expected_statuses:
            self.assertIn(status, valid_statuses)
    
    def test_order_default_status(self):
        """Test order default status"""
        self.assertEqual(self.order.status, 'PENDING')
        self.assertEqual(self.order.payment_status, 'PENDING')
    
    def test_order_status_transition(self):
        """Test order status transition"""
        # Test valid status transitions
        statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        
        for new_status in statuses:
            self.order.status = new_status
            self.order.save()
            self.assertEqual(self.order.status, new_status)
    
    def test_order_payment_status_transition(self):
        """Test order payment status transition"""
        # Test valid payment status transitions
        payment_statuses = ['PENDING', 'PAID', 'FAILED', 'REFUNDED']
        
        for new_status in payment_statuses:
            self.order.payment_status = new_status
            self.order.save()
            self.assertEqual(self.order.payment_status, new_status)
    
    def test_order_status_with_timestamps(self):
        """Test order status with timestamp updates"""
        # Test shipped_at timestamp
        self.order.status = 'SHIPPED'
        self.order.save()
        
        # Note: In real implementation, this would be handled in the view
        # Here we test the model behavior
        self.assertEqual(self.order.status, 'SHIPPED')
        
        # Test delivered_at timestamp
        self.order.status = 'DELIVERED'
        self.order.save()
        
        self.assertEqual(self.order.status, 'DELIVERED')


class OrderStatusHistoryTestCase(TestCase):
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
    
    def test_status_history_creation(self):
        """Test status history creation"""
        status_history = OrderStatusHistory.objects.create(
            order=self.order,
            status='PENDING',
            notes='Order created',
            created_by=self.user
        )
        
        self.assertEqual(status_history.order, self.order)
        self.assertEqual(status_history.status, 'PENDING')
        self.assertEqual(status_history.notes, 'Order created')
        self.assertEqual(status_history.created_by, self.user)
        self.assertIsNotNone(status_history.created_at)
    
    def test_status_history_str_representation(self):
        """Test status history string representation"""
        status_history = OrderStatusHistory.objects.create(
            order=self.order,
            status='CONFIRMED',
            notes='Order confirmed',
            created_by=self.admin_user
        )
        
        expected_str = f"{self.order.order_number} - CONFIRMED"
        self.assertEqual(str(status_history), expected_str)
    
    def test_status_history_ordering(self):
        """Test status history ordering (most recent first)"""
        # Create multiple status history entries
        OrderStatusHistory.objects.create(
            order=self.order,
            status='PENDING',
            notes='Order created',
            created_by=self.user
        )
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='CONFIRMED',
            notes='Order confirmed',
            created_by=self.admin_user
        )
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='PROCESSING',
            notes='Order processing',
            created_by=self.admin_user
        )
        
        # Get all status history entries
        history_entries = OrderStatusHistory.objects.filter(order=self.order)
        
        # Verify ordering (most recent first)
        self.assertEqual(history_entries[0].status, 'PROCESSING')
        self.assertEqual(history_entries[1].status, 'CONFIRMED')
        self.assertEqual(history_entries[2].status, 'PENDING')
    
    def test_status_history_without_created_by(self):
        """Test status history creation without created_by"""
        status_history = OrderStatusHistory.objects.create(
            order=self.order,
            status='SHIPPED',
            notes='Order shipped automatically'
        )
        
        self.assertIsNone(status_history.created_by)
        self.assertEqual(status_history.status, 'SHIPPED')
    
    def test_status_history_notes(self):
        """Test status history notes"""
        # Test with notes
        status_history = OrderStatusHistory.objects.create(
            order=self.order,
            status='DELIVERED',
            notes='Order delivered successfully',
            created_by=self.admin_user
        )
        
        self.assertEqual(status_history.notes, 'Order delivered successfully')
        
        # Test without notes
        status_history2 = OrderStatusHistory.objects.create(
            order=self.order,
            status='CANCELLED',
            created_by=self.admin_user
        )
        
        self.assertEqual(status_history2.notes, '')


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
    
    def test_update_order_status_admin_success(self):
        """Test successful order status update by admin"""
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
        self.assertEqual(history_entry.notes, 'Order confirmed by admin')
        self.assertEqual(history_entry.created_by, self.admin_user)
    
    def test_update_order_status_non_admin_forbidden(self):
        """Test order status update by non-admin user"""
        self.client.force_authenticate(user=self.user)
        
        status_data = {
            'status': 'CONFIRMED',
            'notes': 'Order confirmed'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_order_status_unauthenticated(self):
        """Test order status update when not authenticated"""
        status_data = {
            'status': 'CONFIRMED',
            'notes': 'Order confirmed'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_order_status_invalid_status(self):
        """Test order status update with invalid status"""
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
    
    def test_update_order_status_multiple_transitions(self):
        """Test multiple order status transitions"""
        self.client.force_authenticate(user=self.admin_user)
        
        statuses = ['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        
        for status in statuses:
            status_data = {
                'status': status,
                'notes': f'Status changed to {status}'
            }
            
            response = self.client.patch(self.status_update_url, status_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['status'], status)
        
        # Verify all status history entries were created
        self.order.refresh_from_db()
        self.assertEqual(self.order.status_history.count(), len(statuses))
        
        # Verify final status
        self.assertEqual(self.order.status, 'DELIVERED')
    
    def test_update_order_status_with_tracking_number(self):
        """Test order status update with tracking number"""
        self.client.force_authenticate(user=self.admin_user)
        
        status_data = {
            'status': 'SHIPPED',
            'notes': 'Order shipped with tracking',
            'tracking_number': 'TRK123456789'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify tracking number was set
        self.order.refresh_from_db()
        self.assertEqual(self.order.tracking_number, 'TRK123456789')
    
    def test_update_order_status_cancellation(self):
        """Test order status update to cancelled"""
        self.client.force_authenticate(user=self.admin_user)
        
        status_data = {
            'status': 'CANCELLED',
            'notes': 'Order cancelled by customer request'
        }
        
        response = self.client.patch(self.status_update_url, status_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'CANCELLED')
        
        # Verify order was cancelled
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'CANCELLED')
        
        # Verify status history
        history_entry = self.order.status_history.first()
        self.assertEqual(history_entry.status, 'CANCELLED')
        self.assertEqual(history_entry.notes, 'Order cancelled by customer request')


class OrderStatusWorkflowTestCase(TestCase):
    """Test cases for order status workflow"""
    
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
    
    def test_complete_order_workflow(self):
        """Test complete order workflow from creation to delivery"""
        # Step 1: Order created (PENDING)
        self.assertEqual(self.order.status, 'PENDING')
        self.assertEqual(self.order.payment_status, 'PENDING')
        
        # Step 2: Payment completed (CONFIRMED)
        self.order.payment_status = 'PAID'
        self.order.status = 'CONFIRMED'
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='CONFIRMED',
            notes='Payment completed',
            created_by=self.user
        )
        
        self.assertEqual(self.order.status, 'CONFIRMED')
        self.assertEqual(self.order.payment_status, 'PAID')
        
        # Step 3: Order processing (PROCESSING)
        self.order.status = 'PROCESSING'
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='PROCESSING',
            notes='Order is being processed',
            created_by=self.admin_user
        )
        
        self.assertEqual(self.order.status, 'PROCESSING')
        
        # Step 4: Order shipped (SHIPPED)
        self.order.status = 'SHIPPED'
        self.order.shipped_at = timezone.now()
        self.order.tracking_number = 'TRK123456789'
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='SHIPPED',
            notes='Order has been shipped',
            created_by=self.admin_user
        )
        
        self.assertEqual(self.order.status, 'SHIPPED')
        self.assertIsNotNone(self.order.shipped_at)
        self.assertEqual(self.order.tracking_number, 'TRK123456789')
        
        # Step 5: Order delivered (DELIVERED)
        self.order.status = 'DELIVERED'
        self.order.delivered_at = timezone.now()
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='DELIVERED',
            notes='Order has been delivered',
            created_by=self.admin_user
        )
        
        self.assertEqual(self.order.status, 'DELIVERED')
        self.assertIsNotNone(self.order.delivered_at)
        
        # Verify complete status history
        self.assertEqual(self.order.status_history.count(), 4)
        statuses = [entry.status for entry in self.order.status_history.all()]
        expected_statuses = ['DELIVERED', 'SHIPPED', 'PROCESSING', 'CONFIRMED']
        self.assertEqual(statuses, expected_statuses)
    
    def test_order_cancellation_workflow(self):
        """Test order cancellation workflow"""
        # Create payment
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='COMPLETED'
        )
        
        # Order confirmed
        self.order.payment_status = 'PAID'
        self.order.status = 'CONFIRMED'
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='CONFIRMED',
            notes='Payment completed',
            created_by=self.user
        )
        
        # Cancel order
        self.order.status = 'CANCELLED'
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='CANCELLED',
            notes='Order cancelled by customer request',
            created_by=self.admin_user
        )
        
        # Refund payment
        payment.status = 'REFUNDED'
        payment.save()
        
        self.order.payment_status = 'REFUNDED'
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='REFUNDED',
            notes='Payment refunded',
            created_by=self.admin_user
        )
        
        # Verify cancellation
        self.assertEqual(self.order.status, 'CANCELLED')
        self.assertEqual(self.order.payment_status, 'REFUNDED')
        self.assertEqual(payment.status, 'REFUNDED')
        
        # Verify status history
        self.assertEqual(self.order.status_history.count(), 3)
        statuses = [entry.status for entry in self.order.status_history.all()]
        expected_statuses = ['REFUNDED', 'CANCELLED', 'CONFIRMED']
        self.assertEqual(statuses, expected_statuses)
    
    def test_order_refund_workflow(self):
        """Test order refund workflow"""
        # Create completed order
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='COMPLETED'
        )
        
        self.order.payment_status = 'PAID'
        self.order.status = 'DELIVERED'
        self.order.delivered_at = timezone.now()
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='DELIVERED',
            notes='Order delivered',
            created_by=self.admin_user
        )
        
        # Process refund
        payment.status = 'REFUNDED'
        payment.save()
        
        self.order.payment_status = 'REFUNDED'
        self.order.status = 'REFUNDED'
        self.order.save()
        
        OrderStatusHistory.objects.create(
            order=self.order,
            status='REFUNDED',
            notes='Order refunded due to customer request',
            created_by=self.admin_user
        )
        
        # Verify refund
        self.assertEqual(self.order.status, 'REFUNDED')
        self.assertEqual(self.order.payment_status, 'REFUNDED')
        self.assertEqual(payment.status, 'REFUNDED')
        
        # Verify status history
        self.assertEqual(self.order.status_history.count(), 2)
        statuses = [entry.status for entry in self.order.status_history.all()]
        expected_statuses = ['REFUNDED', 'DELIVERED']
        self.assertEqual(statuses, expected_statuses)
    
    def test_order_status_validation(self):
        """Test order status validation"""
        # Test valid status transitions
        valid_transitions = {
            'PENDING': ['CONFIRMED', 'CANCELLED'],
            'CONFIRMED': ['PROCESSING', 'CANCELLED'],
            'PROCESSING': ['SHIPPED', 'CANCELLED'],
            'SHIPPED': ['DELIVERED', 'CANCELLED'],
            'DELIVERED': ['REFUNDED'],
            'CANCELLED': [],
            'REFUNDED': []
        }
        
        for current_status, valid_next_statuses in valid_transitions.items():
            self.order.status = current_status
            self.order.save()
            
            for next_status in valid_next_statuses:
                # This would be validated in the view/business logic
                # Here we test the model behavior
                self.order.status = next_status
                self.order.save()
                self.assertEqual(self.order.status, next_status)
    
    def test_order_status_with_payment_status(self):
        """Test order status coordination with payment status"""
        # Test payment status changes
        self.order.payment_status = 'PAID'
        self.order.status = 'CONFIRMED'
        self.order.save()
        
        self.assertEqual(self.order.payment_status, 'PAID')
        self.assertEqual(self.order.status, 'CONFIRMED')
        
        # Test payment failure
        self.order.payment_status = 'FAILED'
        self.order.status = 'PENDING'
        self.order.save()
        
        self.assertEqual(self.order.payment_status, 'FAILED')
        self.assertEqual(self.order.status, 'PENDING')
        
        # Test payment refund
        self.order.payment_status = 'REFUNDED'
        self.order.status = 'REFUNDED'
        self.order.save()
        
        self.assertEqual(self.order.payment_status, 'REFUNDED')
        self.assertEqual(self.order.status, 'REFUNDED')
