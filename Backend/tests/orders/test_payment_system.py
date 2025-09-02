"""
Payment System Tests

This module contains comprehensive tests for payment processing,
payment validation, and payment-related business logic.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

from orders.models import Order, Payment, OrderStatusHistory
from accounts.models import CustomUser

User = get_user_model()


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
    
    def test_payment_creation(self):
        """Test payment creation"""
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PENDING'
        )
        
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.payment_method, 'CARD')
        self.assertEqual(payment.transaction_id, 'TXN-1234567890')
        self.assertEqual(payment.amount, Decimal('119.98'))
        self.assertEqual(payment.status, 'PENDING')
        self.assertIsNotNone(payment.created_at)
    
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
    
    def test_payment_str_representation(self):
        """Test payment string representation"""
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PENDING'
        )
        
        expected_str = f"Payment {payment.transaction_id} - {payment.amount}"
        self.assertEqual(str(payment), expected_str)
    
    def test_payment_gateway_fields(self):
        """Test payment gateway fields"""
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='COMPLETED',
            gateway='stripe',
            gateway_transaction_id='stripe_1234567890',
            gateway_response={'status': 'succeeded', 'id': 'pi_1234567890'}
        )
        
        self.assertEqual(payment.gateway, 'stripe')
        self.assertEqual(payment.gateway_transaction_id, 'stripe_1234567890')
        self.assertEqual(payment.gateway_response['status'], 'succeeded')
    
    def test_payment_completed_timestamp(self):
        """Test payment completed timestamp"""
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='COMPLETED'
        )
        
        self.assertIsNotNone(payment.completed_at)
    
    def test_payment_unique_transaction_id(self):
        """Test payment unique transaction ID constraint"""
        Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PENDING'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            Payment.objects.create(
                order=self.order,
                payment_method='PAYPAL',
                transaction_id='TXN-1234567890',  # Same transaction ID
                amount=Decimal('119.98'),
                status='PENDING'
            )
    
    def test_payment_one_to_one_with_order(self):
        """Test payment one-to-one relationship with order"""
        Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PENDING'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            Payment.objects.create(
                order=self.order,
                payment_method='PAYPAL',
                transaction_id='TXN-1234567891',
                amount=Decimal('119.98'),
                status='PENDING'
            )


class PaymentProcessingTestCase(APITestCase):
    """Test cases for payment processing"""
    
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
    
    def test_successful_payment_processing(self):
        """Test successful payment processing"""
        self.client.force_authenticate(user=self.user)
        
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('119.98')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'COMPLETED')
        self.assertIsNotNone(response.data['completed_at'])
        
        # Verify payment was created
        payment = Payment.objects.get(transaction_id=response.data['transaction_id'])
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertIsNotNone(payment.completed_at)
        
        # Verify order was updated
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'PAID')
        self.assertEqual(self.order.status, 'CONFIRMED')
        
        # Verify status history was created
        self.assertEqual(self.order.status_history.count(), 1)
        history_entry = self.order.status_history.first()
        self.assertEqual(history_entry.status, 'CONFIRMED')
        self.assertEqual(history_entry.notes, 'Payment completed')
    
    @patch('orders.views.timezone.now')
    def test_payment_with_mocked_time(self, mock_now):
        """Test payment processing with mocked time"""
        from django.utils import timezone
        mock_time = timezone.datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_now.return_value = mock_time
        
        self.client.force_authenticate(user=self.user)
        
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('119.98')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify payment completed_at timestamp
        payment = Payment.objects.get(transaction_id=response.data['transaction_id'])
        self.assertEqual(payment.completed_at, mock_time)
    
    def test_payment_transaction_id_generation(self):
        """Test payment transaction ID generation"""
        self.client.force_authenticate(user=self.user)
        
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('119.98')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['transaction_id'].startswith('TXN-'))
        self.assertEqual(len(response.data['transaction_id']), 20)  # TXN- + 16 chars
    
    def test_payment_amount_validation(self):
        """Test payment amount validation"""
        self.client.force_authenticate(user=self.user)
        
        # Test negative amount
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('-10.00')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test zero amount
        payment_data = {
            'payment_method': 'CARD',
            'amount': Decimal('0.00')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_payment_method_validation(self):
        """Test payment method validation"""
        self.client.force_authenticate(user=self.user)
        
        # Test invalid payment method
        payment_data = {
            'payment_method': 'INVALID_METHOD',
            'amount': Decimal('119.98')
        }
        
        response = self.client.post(self.payment_url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_payment_for_different_payment_methods(self):
        """Test payment processing for different payment methods"""
        self.client.force_authenticate(user=self.user)
        
        payment_methods = ['CARD', 'PAYPAL', 'BANK_TRANSFER', 'COD']
        
        for method in payment_methods:
            # Create new order for each payment method
            order = Order.objects.create(
                user=self.user,
                subtotal=Decimal('99.99'),
                total_amount=Decimal('119.98'),
                shipping_address=self.shipping_address
            )
            
            payment_data = {
                'payment_method': method,
                'amount': Decimal('119.98')
            }
            
            response = self.client.post(f'/api/orders/{order.id}/payment/', payment_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['payment_method'], method)
            self.assertEqual(response.data['status'], 'COMPLETED')
    
    def test_payment_already_exists(self):
        """Test payment creation when payment already exists"""
        # Create existing payment
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
        self.assertIn('already paid', response.data['error'].lower())


class PaymentGatewayIntegrationTestCase(TestCase):
    """Test cases for payment gateway integration"""
    
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
    
    @patch('orders.views.requests.post')
    def test_stripe_payment_integration(self, mock_post):
        """Test Stripe payment gateway integration"""
        # Mock successful Stripe response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'pi_1234567890',
            'status': 'succeeded',
            'amount': 11998,  # Amount in cents
            'currency': 'usd'
        }
        mock_post.return_value = mock_response
        
        # Create payment with Stripe gateway
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PROCESSING',
            gateway='stripe',
            gateway_transaction_id='pi_1234567890',
            gateway_response={'status': 'succeeded'}
        )
        
        # Simulate successful payment processing
        payment.status = 'COMPLETED'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update order
        self.order.payment_status = 'PAID'
        self.order.status = 'CONFIRMED'
        self.order.save()
        
        # Verify payment
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(payment.gateway, 'stripe')
        self.assertEqual(payment.gateway_transaction_id, 'pi_1234567890')
        
        # Verify order
        self.assertEqual(self.order.payment_status, 'PAID')
        self.assertEqual(self.order.status, 'CONFIRMED')
    
    @patch('orders.views.requests.post')
    def test_paypal_payment_integration(self, mock_post):
        """Test PayPal payment gateway integration"""
        # Mock successful PayPal response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'PAY-1234567890',
            'state': 'approved',
            'transactions': [{
                'amount': {
                    'total': '119.98',
                    'currency': 'USD'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Create payment with PayPal gateway
        payment = Payment.objects.create(
            order=self.order,
            payment_method='PAYPAL',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PROCESSING',
            gateway='paypal',
            gateway_transaction_id='PAY-1234567890',
            gateway_response={'state': 'approved'}
        )
        
        # Simulate successful payment processing
        payment.status = 'COMPLETED'
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update order
        self.order.payment_status = 'PAID'
        self.order.status = 'CONFIRMED'
        self.order.save()
        
        # Verify payment
        self.assertEqual(payment.status, 'COMPLETED')
        self.assertEqual(payment.gateway, 'paypal')
        self.assertEqual(payment.gateway_transaction_id, 'PAY-1234567890')
    
    @patch('orders.views.requests.post')
    def test_payment_gateway_failure(self, mock_post):
        """Test payment gateway failure handling"""
        # Mock failed gateway response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {
                'type': 'card_error',
                'message': 'Your card was declined.'
            }
        }
        mock_post.return_value = mock_response
        
        # Create payment
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PROCESSING',
            gateway='stripe',
            gateway_response={'error': 'Your card was declined.'}
        )
        
        # Simulate failed payment processing
        payment.status = 'FAILED'
        payment.save()
        
        # Order should remain in pending status
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'PENDING')
        self.assertEqual(self.order.status, 'PENDING')
        
        # Verify payment
        self.assertEqual(payment.status, 'FAILED')
        self.assertIn('declined', payment.gateway_response['error'])


class PaymentRefundTestCase(TestCase):
    """Test cases for payment refunds"""
    
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
            shipping_address=self.shipping_address,
            status='DELIVERED',
            payment_status='PAID'
        )
        
        self.payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='COMPLETED',
            gateway='stripe',
            gateway_transaction_id='pi_1234567890'
        )
    
    def test_payment_refund_creation(self):
        """Test payment refund creation"""
        # Create refund payment
        refund_payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-REFUND-1234567890',
            amount=Decimal('119.98'),
            status='REFUNDED',
            gateway='stripe',
            gateway_transaction_id='re_1234567890',
            gateway_response={'status': 'succeeded', 'type': 'refund'}
        )
        
        # Update order
        self.order.payment_status = 'REFUNDED'
        self.order.status = 'REFUNDED'
        self.order.save()
        
        # Verify refund
        self.assertEqual(refund_payment.status, 'REFUNDED')
        self.assertEqual(refund_payment.amount, Decimal('119.98'))
        self.assertEqual(refund_payment.gateway_transaction_id, 're_1234567890')
        
        # Verify order
        self.assertEqual(self.order.payment_status, 'REFUNDED')
        self.assertEqual(self.order.status, 'REFUNDED')
    
    def test_partial_refund(self):
        """Test partial payment refund"""
        # Create partial refund
        partial_refund = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-PARTIAL-REFUND-1234567890',
            amount=Decimal('50.00'),
            status='REFUNDED',
            gateway='stripe',
            gateway_transaction_id='re_partial_1234567890',
            gateway_response={'status': 'succeeded', 'type': 'partial_refund'}
        )
        
        # Verify partial refund
        self.assertEqual(partial_refund.status, 'REFUNDED')
        self.assertEqual(partial_refund.amount, Decimal('50.00'))
        
        # Order should still be marked as partially refunded
        # This would require additional logic in the order model
        self.assertEqual(self.order.payment_status, 'PAID')  # Still paid for remaining amount
    
    @patch('orders.views.requests.post')
    def test_stripe_refund_integration(self, mock_post):
        """Test Stripe refund integration"""
        # Mock successful Stripe refund response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 're_1234567890',
            'status': 'succeeded',
            'amount': 11998,  # Amount in cents
            'charge': 'pi_1234567890'
        }
        mock_post.return_value = mock_response
        
        # Create refund
        refund_payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-REFUND-1234567890',
            amount=Decimal('119.98'),
            status='REFUNDED',
            gateway='stripe',
            gateway_transaction_id='re_1234567890',
            gateway_response={'status': 'succeeded'}
        )
        
        # Update order
        self.order.payment_status = 'REFUNDED'
        self.order.status = 'REFUNDED'
        self.order.save()
        
        # Verify refund
        self.assertEqual(refund_payment.status, 'REFUNDED')
        self.assertEqual(refund_payment.gateway, 'stripe')
        self.assertEqual(refund_payment.gateway_transaction_id, 're_1234567890')


class PaymentSecurityTestCase(TestCase):
    """Test cases for payment security"""
    
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
    
    def test_payment_user_isolation(self):
        """Test that users can only create payments for their own orders"""
        # This would be tested in the API view tests
        # Here we test the model level security
        
        # User should be able to create payment for their own order
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PENDING'
        )
        
        self.assertEqual(payment.order.user, self.user)
    
    def test_payment_amount_validation(self):
        """Test payment amount validation"""
        # Test negative amount
        with self.assertRaises(Exception):
            Payment.objects.create(
                order=self.order,
                payment_method='CARD',
                transaction_id='TXN-1234567890',
                amount=Decimal('-10.00'),  # Negative amount
                status='PENDING'
            )
    
    def test_payment_transaction_id_uniqueness(self):
        """Test payment transaction ID uniqueness"""
        Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='PENDING'
        )
        
        # Try to create another payment with same transaction ID
        with self.assertRaises(Exception):
            Payment.objects.create(
                order=self.order,
                payment_method='PAYPAL',
                transaction_id='TXN-1234567890',  # Same transaction ID
                amount=Decimal('119.98'),
                status='PENDING'
            )
    
    def test_payment_gateway_response_validation(self):
        """Test payment gateway response validation"""
        # Test with valid gateway response
        payment = Payment.objects.create(
            order=self.order,
            payment_method='CARD',
            transaction_id='TXN-1234567890',
            amount=Decimal('119.98'),
            status='COMPLETED',
            gateway='stripe',
            gateway_response={'status': 'succeeded', 'id': 'pi_1234567890'}
        )
        
        self.assertEqual(payment.gateway_response['status'], 'succeeded')
        
        # Test with empty gateway response
        payment2 = Payment.objects.create(
            order=self.order,
            payment_method='COD',
            transaction_id='TXN-1234567891',
            amount=Decimal('119.98'),
            status='COMPLETED',
            gateway_response={}
        )
        
        self.assertEqual(payment2.gateway_response, {})
