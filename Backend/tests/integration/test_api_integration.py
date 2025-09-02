"""
API Integration Tests

This module contains comprehensive integration tests for API endpoints
testing the complete flow from authentication to order completion.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
import json

from accounts.models import CustomUser
from products.models import Product, Category, Seller
from orders.models import Cart, CartItem, Order, OrderItem

User = get_user_model()


class CompleteUserJourneyTestCase(APITestCase):
    """Test complete user journey from registration to order completion"""
    
    def setUp(self):
        """Set up test data"""
        self.seller_user = CustomUser.objects.create_user(
            phone='9876543210',
            password='testpass123',
            first_name='Seller',
            last_name='User',
            user_type='SELLER'
        )
        
        self.seller = Seller.objects.create(
            name='Test Seller',
            email='seller@test.com',
            phone='1234567890',
            address='Test Address',
            user=self.seller_user
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
    
    def test_complete_user_journey(self):
        """Test complete user journey from registration to order completion"""
        
        # Step 1: User Registration
        register_data = {
            'phone': '1234567890',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1990-01-01',
            'user_type': 'CUSTOMER'
        }
        
        response = self.client.post('/accounts/register/', register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 2: User Login
        login_data = {
            'phone': '1234567890',
            'password': 'testpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        
        token = response.data['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Step 3: Browse Products
        response = self.client.get('/api/products/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        
        # Step 4: Get Product Details
        response = self.client.get(f'/api/products/{self.product1.id}/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Product 1')
        
        # Step 5: Add Items to Cart
        cart_data = {
            'product_id': self.product1.id,
            'quantity': 2
        }
        
        response = self.client.post('/api/orders/cart/', cart_data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        cart_data = {
            'product_id': self.product2.id,
            'quantity': 1
        }
        
        response = self.client.post('/api/orders/cart/', cart_data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Step 6: View Cart
        response = self.client.get('/api/orders/cart/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['total_items'], 3)
        
        # Step 7: Create Order
        order_data = {
            'shipping_address': {
                'street': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'USA'
            },
            'notes': 'Please deliver after 5 PM'
        }
        
        response = self.client.post('/api/orders/orders/', order_data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_number', response.data)
        
        order_id = response.data['id']
        
        # Step 8: View Order Details
        response = self.client.get(f'/api/orders/orders/{order_id}/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PENDING')
        
        # Step 9: View Order List
        response = self.client.get('/api/orders/orders/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Step 10: Verify Cart is Empty After Order
        response = self.client.get('/api/orders/cart/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 0)
    
    def test_search_and_filter_integration(self):
        """Test search and filter functionality integration"""
        
        # Create user and login
        user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        login_data = {
            'phone': '1234567890',
            'password': 'testpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data, format='json')
        token = response.data['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test search functionality
        response = self.client.get('/api/search/?q=Product', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        
        # Test filtering by category
        response = self.client.get('/api/products/?category=Electronics', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Test filtering by price range
        response = self.client.get('/api/products/?min_price=100&max_price=200', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Product 2')
        
        # Test sorting
        response = self.client.get('/api/products/?sort_by=price_low', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(product['price']) for product in response.data['results']]
        self.assertEqual(prices, sorted(prices))
    
    def test_authentication_flow_integration(self):
        """Test complete authentication flow integration"""
        
        # Test registration
        register_data = {
            'phone': '1234567890',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1990-01-01',
            'user_type': 'CUSTOMER'
        }
        
        response = self.client.post('/accounts/register/', register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test login
        login_data = {
            'phone': '1234567890',
            'password': 'testpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        
        # Test protected endpoint access
        headers = {'Authorization': f'Bearer {token}'}
        response = self.client.get('/api/orders/cart/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test logout (if implemented)
        # response = self.client.post('/accounts/logout/', headers=headers)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test access after logout (should fail)
        # response = self.client.get('/api/orders/cart/', headers=headers)
        # self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_password_reset_flow_integration(self):
        """Test complete password reset flow integration"""
        
        # Create user
        user = CustomUser.objects.create_user(
            phone='1234567890',
            password='oldpassword123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        # Step 1: Request password reset
        data = {'phone': '1234567890'}
        response = self.client.post('/accounts/forgot-password/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('otp', response.data)
        
        # Step 2: Verify OTP
        otp = response.data['otp']
        verify_data = {
            'phone': '1234567890',
            'otp': otp
        }
        
        with self.settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}):
            response = self.client.post('/accounts/verify-otp/', verify_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 3: Reset password
        reset_data = {
            'phone': '1234567890',
            'password': 'newpassword123'
        }
        
        with self.settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}):
            response = self.client.post('/accounts/reset-password/', reset_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 4: Login with new password
        login_data = {
            'phone': '1234567890',
            'password': 'newpassword123'
        }
        
        response = self.client.post('/accounts/login/', login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_error_handling_integration(self):
        """Test error handling across different endpoints"""
        
        # Test invalid authentication
        headers = {'Authorization': 'Bearer invalid_token'}
        response = self.client.get('/api/orders/cart/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test invalid product ID
        response = self.client.get('/api/products/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test invalid order ID
        user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        login_data = {
            'phone': '1234567890',
            'password': 'testpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data, format='json')
        token = response.data['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        response = self.client.get('/api/orders/orders/99999/', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test invalid data submission
        invalid_data = {
            'product_id': 99999,
            'quantity': -1
        }
        
        response = self.client.post('/api/orders/cart/', invalid_data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_performance_integration(self):
        """Test performance aspects of API integration"""
        
        # Create user and login
        user = CustomUser.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        login_data = {
            'phone': '1234567890',
            'password': 'testpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data, format='json')
        token = response.data['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test multiple rapid requests
        import time
        start_time = time.time()
        
        for _ in range(10):
            response = self.client.get('/api/products/', headers=headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(duration, 5.0)  # 5 seconds for 10 requests
        
        print(f"Performance test: 10 requests completed in {duration:.2f} seconds")


class CrossFeatureIntegrationTestCase(APITestCase):
    """Test integration between different features"""
    
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
    
    def test_product_cart_order_integration(self):
        """Test integration between product, cart, and order features"""
        
        # Login
        login_data = {
            'phone': '1234567890',
            'password': 'testpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data, format='json')
        token = response.data['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Add product to cart
        cart_data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        
        response = self.client.post('/api/orders/cart/', cart_data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify product stock is not affected by cart addition
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 100)
        
        # Create order
        order_data = {
            'shipping_address': {
                'street': '123 Main St',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'USA'
            }
        }
        
        response = self.client.post('/api/orders/orders/', order_data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify order was created with correct items
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        
        self.assertEqual(order_items.count(), 1)
        self.assertEqual(order_items.first().product, self.product)
        self.assertEqual(order_items.first().quantity, 2)
    
    def test_search_cart_integration(self):
        """Test integration between search and cart features"""
        
        # Login
        login_data = {
            'phone': '1234567890',
            'password': 'testpass123'
        }
        
        response = self.client.post('/accounts/login/', login_data, format='json')
        token = response.data['token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Search for products
        response = self.client.get('/api/search/?q=Test', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Add found product to cart
        if response.data['results']:
            product_id = response.data['results'][0]['id']
            
            cart_data = {
                'product_id': product_id,
                'quantity': 1
            }
            
            response = self.client.post('/api/orders/cart/', cart_data, format='json', headers=headers)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Verify item is in cart
            response = self.client.get('/api/orders/cart/', headers=headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['items']), 1)
