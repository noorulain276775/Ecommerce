"""
Shopping Cart Tests

This module contains comprehensive tests for shopping cart functionality
including adding, updating, removing items, and cart management.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
import json

from orders.models import Cart, CartItem
from products.models import Product, Category, Seller
from accounts.models import CustomUser

User = get_user_model()


class CartModelTestCase(TestCase):
    """Test cases for Cart model"""
    
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
        
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_creation(self):
        """Test cart creation"""
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.total_amount, Decimal('0.00'))
        self.assertFalse(self.cart.is_empty)
    
    def test_cart_str_representation(self):
        """Test cart string representation"""
        expected_str = f"Cart for {self.user.phone}"
        self.assertEqual(str(self.cart), expected_str)
    
    def test_cart_is_empty_property(self):
        """Test cart is_empty property"""
        # Empty cart should return True for is_empty
        self.assertTrue(self.cart.is_empty)
        
        # Add item to cart
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        # Cart with items should return False for is_empty
        self.cart.refresh_from_db()
        self.assertFalse(self.cart.is_empty)
    
    def test_cart_total_calculation(self):
        """Test cart total calculation"""
        # Add items to cart
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        # Refresh cart from database
        self.cart.refresh_from_db()
        
        expected_total = Decimal('199.98')  # 99.99 * 2
        self.assertEqual(self.cart.total_amount, expected_total)
        self.assertEqual(self.cart.total_items, 2)
    
    def test_cart_clear(self):
        """Test clearing cart"""
        # Add items to cart
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        # Clear cart
        self.cart.clear()
        
        # Verify cart is empty
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.total_amount, Decimal('0.00'))
        self.assertTrue(self.cart.is_empty)
        
        # Verify cart items are deleted
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 0)


class CartItemModelTestCase(TestCase):
    """Test cases for CartItem model"""
    
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
        
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
    
    def test_cart_item_creation(self):
        """Test cart item creation"""
        self.assertEqual(self.cart_item.cart, self.cart)
        self.assertEqual(self.cart_item.product, self.product)
        self.assertEqual(self.cart_item.quantity, 2)
    
    def test_cart_item_str_representation(self):
        """Test cart item string representation"""
        expected_str = f"{self.product.title} x {self.cart_item.quantity}"
        self.assertEqual(str(self.cart_item), expected_str)
    
    def test_cart_item_total_price(self):
        """Test cart item total price calculation"""
        expected_total = Decimal('199.98')  # 99.99 * 2
        self.assertEqual(self.cart_item.total_price, expected_total)
    
    def test_cart_item_unit_price(self):
        """Test cart item unit price"""
        self.assertEqual(self.cart_item.unit_price, Decimal('99.99'))
    
    def test_cart_item_update_quantity(self):
        """Test updating cart item quantity"""
        self.cart_item.quantity = 5
        self.cart_item.save()
        
        self.assertEqual(self.cart_item.quantity, 5)
        expected_total = Decimal('499.95')  # 99.99 * 5
        self.assertEqual(self.cart_item.total_price, expected_total)


class CartViewTestCase(APITestCase):
    """Test cases for Cart API views"""
    
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
        
        self.cart = Cart.objects.create(user=self.user)
        
        self.cart_url = '/api/orders/cart/'
        self.cart_item_url = '/api/orders/cart/items/'
    
    def test_get_cart_authenticated(self):
        """Test getting cart when authenticated"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.cart_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertIn('total_items', response.data)
        self.assertIn('total_amount', response.data)
        self.assertEqual(response.data['total_items'], 0)
        self.assertEqual(response.data['total_amount'], '0.00')
    
    def test_get_cart_unauthenticated(self):
        """Test getting cart when not authenticated"""
        response = self.client.get(self.cart_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_add_item_to_cart(self):
        """Test adding item to cart"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'product_id': self.product1.id,
            'quantity': 2
        }
        
        response = self.client.post(self.cart_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        
        # Verify item was added to cart
        cart_item = CartItem.objects.get(cart=self.cart, product=self.product1)
        self.assertEqual(cart_item.quantity, 2)
        
        # Verify cart totals
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total_items, 2)
        self.assertEqual(self.cart.total_amount, Decimal('199.98'))
    
    def test_add_existing_item_to_cart(self):
        """Test adding existing item to cart (should update quantity)"""
        self.client.force_authenticate(user=self.user)
        
        # First, add item to cart
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=1
        )
        
        # Add same item again
        data = {
            'product_id': self.product1.id,
            'quantity': 2
        }
        
        response = self.client.post(self.cart_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify quantity was updated
        cart_item = CartItem.objects.get(cart=self.cart, product=self.product1)
        self.assertEqual(cart_item.quantity, 3)  # 1 + 2
        
        # Verify cart totals
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total_items, 3)
        self.assertEqual(self.cart.total_amount, Decimal('299.97'))
    
    def test_add_item_exceeding_stock(self):
        """Test adding item exceeding available stock"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'product_id': self.product1.id,
            'quantity': 150  # More than available stock (100)
        }
        
        response = self.client.post(self.cart_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data['error'].lower())
    
    def test_add_nonexistent_product(self):
        """Test adding non-existent product to cart"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'product_id': 99999,
            'quantity': 1
        }
        
        response = self.client.post(self.cart_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_item_with_invalid_quantity(self):
        """Test adding item with invalid quantity"""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'product_id': self.product1.id,
            'quantity': 0  # Invalid quantity
        }
        
        response = self.client.post(self.cart_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_cart_item_quantity(self):
        """Test updating cart item quantity"""
        self.client.force_authenticate(user=self.user)
        
        # Add item to cart
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        # Update quantity
        data = {'quantity': 5}
        response = self.client.put(f'{self.cart_item_url}{cart_item.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify quantity was updated
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
        
        # Verify cart totals
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total_items, 5)
        self.assertEqual(self.cart.total_amount, Decimal('499.95'))
    
    def test_update_cart_item_exceeding_stock(self):
        """Test updating cart item quantity exceeding stock"""
        self.client.force_authenticate(user=self.user)
        
        # Add item to cart
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        # Try to update to quantity exceeding stock
        data = {'quantity': 150}
        response = self.client.put(f'{self.cart_item_url}{cart_item.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data['error'].lower())
    
    def test_remove_cart_item(self):
        """Test removing cart item"""
        self.client.force_authenticate(user=self.user)
        
        # Add item to cart
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        # Remove item
        response = self.client.delete(f'{self.cart_item_url}{cart_item.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify item was removed
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
        
        # Verify cart totals
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.total_amount, Decimal('0.00'))
    
    def test_remove_nonexistent_cart_item(self):
        """Test removing non-existent cart item"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.delete(f'{self.cart_item_url}99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_clear_cart(self):
        """Test clearing entire cart"""
        self.client.force_authenticate(user=self.user)
        
        # Add multiple items to cart
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=1
        )
        
        # Clear cart
        response = self.client.delete(self.cart_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify cart is empty
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.total_amount, Decimal('0.00'))
        
        # Verify all cart items were removed
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 0)
    
    def test_cart_with_multiple_items(self):
        """Test cart with multiple different items"""
        self.client.force_authenticate(user=self.user)
        
        # Add multiple items
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=1
        )
        
        # Get cart
        response = self.client.get(self.cart_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['total_items'], 3)
        
        # Calculate expected total
        expected_total = Decimal('349.97')  # (99.99 * 2) + (149.99 * 1)
        self.assertEqual(response.data['total_amount'], str(expected_total))
    
    def test_cart_item_serialization(self):
        """Test cart item serialization"""
        self.client.force_authenticate(user=self.user)
        
        # Add item to cart
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=3
        )
        
        # Get cart
        response = self.client.get(self.cart_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cart_item_data = response.data['items'][0]
        self.assertIn('id', cart_item_data)
        self.assertIn('product', cart_item_data)
        self.assertIn('quantity', cart_item_data)
        self.assertIn('unit_price', cart_item_data)
        self.assertIn('total_price', cart_item_data)
        
        # Verify product data is included
        self.assertIn('id', cart_item_data['product'])
        self.assertIn('title', cart_item_data['product'])
        self.assertIn('price', cart_item_data['product'])
        self.assertIn('image', cart_item_data['product'])
    
    def test_cart_permissions(self):
        """Test cart permissions - users can only access their own cart"""
        # Create another user
        other_user = CustomUser.objects.create_user(
            phone='9876543210',
            password='testpass123',
            first_name='Other',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        # Create cart for other user
        other_cart = Cart.objects.create(user=other_user)
        CartItem.objects.create(
            cart=other_cart,
            product=self.product1,
            quantity=1
        )
        
        # Authenticate as first user
        self.client.force_authenticate(user=self.user)
        
        # Try to access other user's cart item
        other_cart_item = CartItem.objects.get(cart=other_cart)
        response = self.client.get(f'{self.cart_item_url}{other_cart_item.id}/')
        
        # Should return 404 (not found) for security
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_cart_item_validation(self):
        """Test cart item validation"""
        self.client.force_authenticate(user=self.user)
        
        # Test with missing product_id
        data = {'quantity': 1}
        response = self.client.post(self.cart_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with missing quantity
        data = {'product_id': self.product1.id}
        response = self.client.post(self.cart_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test with negative quantity
        data = {
            'product_id': self.product1.id,
            'quantity': -1
        }
        response = self.client.post(self.cart_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cart_with_out_of_stock_product(self):
        """Test cart behavior with out of stock product"""
        # Create product with no stock
        out_of_stock_product = Product.objects.create(
            title='Out of Stock Product',
            description='Out of Stock Description',
            price=99.99,
            category=self.category,
            seller=self.seller,
            stock=0
        )
        
        self.client.force_authenticate(user=self.user)
        
        # Try to add out of stock product
        data = {
            'product_id': out_of_stock_product.id,
            'quantity': 1
        }
        
        response = self.client.post(self.cart_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', response.data['error'].lower())
    
    def test_cart_item_update_with_zero_quantity(self):
        """Test updating cart item quantity to zero (should remove item)"""
        self.client.force_authenticate(user=self.user)
        
        # Add item to cart
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        # Update quantity to zero
        data = {'quantity': 0}
        response = self.client.put(f'{self.cart_item_url}{cart_item.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify item was removed
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
        
        # Verify cart totals
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.total_amount, Decimal('0.00'))
