"""
Product CRUD Tests

This module contains comprehensive tests for product CRUD operations
including creation, reading, updating, and deletion of products.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import json

from products.models import Product, Category, Seller
from products.serializers import ProductSerializer
from products.views import ProductView, ProductDetailView

User = get_user_model()


class ProductModelTestCase(TestCase):
    """Test cases for Product model"""
    
    def setUp(self):
        """Set up test data"""
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
    
    def test_product_creation(self):
        """Test product creation"""
        self.assertEqual(self.product.title, 'Test Product')
        self.assertEqual(self.product.price, 99.99)
        self.assertEqual(self.product.stock, 100)
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.seller, self.seller)
    
    def test_product_str_representation(self):
        """Test product string representation"""
        expected_str = f"{self.product.title} - {self.product.seller.name}"
        self.assertEqual(str(self.product), expected_str)
    
    def test_product_slug_generation(self):
        """Test automatic slug generation"""
        self.assertIsNotNone(self.product.slug)
        self.assertTrue(len(self.product.slug) > 0)
    
    def test_product_discount_calculation(self):
        """Test discount calculation"""
        self.product.discount_percentage = 10.0
        self.product.save()
        
        expected_discounted_price = 99.99 * (1 - 10.0 / 100)
        self.assertEqual(self.product.discounted_price, expected_discounted_price)
    
    def test_product_availability(self):
        """Test product availability logic"""
        # Product with stock should be available
        self.assertTrue(self.product.is_available)
        
        # Product with no stock should not be available
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_available)
    
    def test_product_featured_flags(self):
        """Test product featured flags"""
        # Test flash sale flag
        self.product.flash_sale = True
        self.product.save()
        self.assertTrue(self.product.flash_sale)
        
        # Test best seller flag
        self.product.best_seller_product = True
        self.product.save()
        self.assertTrue(self.product.best_seller_product)
        
        # Test featured product flag
        self.product.featured_product = True
        self.product.save()
        self.assertTrue(self.product.featured_product)


class ProductSerializerTestCase(TestCase):
    """Test cases for Product serializer"""
    
    def setUp(self):
        """Set up test data"""
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
        
        self.product_data = {
            'title': 'Test Product',
            'description': 'Test Description',
            'price': 99.99,
            'category': self.category.id,
            'seller': self.seller.id,
            'stock': 100,
            'discount_percentage': 10.0
        }
    
    def test_product_serialization(self):
        """Test product serialization"""
        product = Product.objects.create(
            title=self.product_data['title'],
            description=self.product_data['description'],
            price=self.product_data['price'],
            category=self.category,
            seller=self.seller,
            stock=self.product_data['stock'],
            discount_percentage=self.product_data['discount_percentage']
        )
        
        serializer = ProductSerializer(product)
        data = serializer.data
        
        self.assertEqual(data['title'], self.product_data['title'])
        self.assertEqual(data['price'], str(self.product_data['price']))
        self.assertEqual(data['stock'], self.product_data['stock'])
        self.assertEqual(data['discount_percentage'], str(self.product_data['discount_percentage']))
    
    def test_product_deserialization(self):
        """Test product deserialization"""
        serializer = ProductSerializer(data=self.product_data)
        self.assertTrue(serializer.is_valid())
        
        product = serializer.save()
        self.assertEqual(product.title, self.product_data['title'])
        self.assertEqual(product.price, self.product_data['price'])
        self.assertEqual(product.stock, self.product_data['stock'])
    
    def test_invalid_product_data(self):
        """Test product deserialization with invalid data"""
        invalid_data = {
            'title': '',  # Empty title
            'price': -10.0,  # Negative price
            'stock': -5,  # Negative stock
        }
        
        serializer = ProductSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertIn('price', serializer.errors)
        self.assertIn('stock', serializer.errors)


class ProductViewTestCase(APITestCase):
    """Test cases for Product API views"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            phone='1234567890',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='CUSTOMER'
        )
        
        self.seller_user = User.objects.create_user(
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
        
        self.product = Product.objects.create(
            title='Test Product',
            description='Test Description',
            price=99.99,
            category=self.category,
            seller=self.seller,
            stock=100
        )
        
        self.products_url = '/api/products/'
        self.product_detail_url = f'/api/products/{self.product.id}/'
    
    def test_get_products_list(self):
        """Test getting list of products"""
        response = self.client.get(self.products_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Product')
    
    def test_get_products_with_pagination(self):
        """Test products list with pagination"""
        # Create multiple products
        for i in range(25):
            Product.objects.create(
                title=f'Product {i}',
                description=f'Description {i}',
                price=10.0 + i,
                category=self.category,
                seller=self.seller,
                stock=50
            )
        
        response = self.client.get(self.products_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(response.data['count'], 26)  # 25 new + 1 existing
    
    def test_get_products_with_filtering(self):
        """Test products list with filtering"""
        # Create products with different categories
        category2 = Category.objects.create(
            name='Books',
            description='Book products'
        )
        
        Product.objects.create(
            title='Book Product',
            description='Book Description',
            price=19.99,
            category=category2,
            seller=self.seller,
            stock=50
        )
        
        # Filter by category
        response = self.client.get(f'{self.products_url}?category=Electronics')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Product')
    
    def test_get_products_with_price_filtering(self):
        """Test products list with price filtering"""
        # Create products with different prices
        Product.objects.create(
            title='Expensive Product',
            description='Expensive Description',
            price=200.0,
            category=self.category,
            seller=self.seller,
            stock=10
        )
        
        Product.objects.create(
            title='Cheap Product',
            description='Cheap Description',
            price=10.0,
            category=self.category,
            seller=self.seller,
            stock=100
        )
        
        # Filter by price range
        response = self.client.get(f'{self.products_url}?min_price=50&max_price=150')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Product')
    
    def test_get_products_with_sorting(self):
        """Test products list with sorting"""
        # Create products with different prices
        Product.objects.create(
            title='Cheap Product',
            description='Cheap Description',
            price=10.0,
            category=self.category,
            seller=self.seller,
            stock=100
        )
        
        Product.objects.create(
            title='Expensive Product',
            description='Expensive Description',
            price=200.0,
            category=self.category,
            seller=self.seller,
            stock=10
        )
        
        # Sort by price ascending
        response = self.client.get(f'{self.products_url}?sort_by=price_low')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(product['price']) for product in response.data['results']]
        self.assertEqual(prices, sorted(prices))
        
        # Sort by price descending
        response = self.client.get(f'{self.products_url}?sort_by=price_high')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(product['price']) for product in response.data['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))
    
    def test_get_product_detail(self):
        """Test getting product detail"""
        response = self.client.get(self.product_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Product')
        self.assertEqual(response.data['price'], '99.99')
        self.assertEqual(response.data['stock'], 100)
    
    def test_get_nonexistent_product(self):
        """Test getting non-existent product"""
        response = self.client.get('/api/products/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_product_authenticated(self):
        """Test creating product when authenticated"""
        self.client.force_authenticate(user=self.seller_user)
        
        product_data = {
            'title': 'New Product',
            'description': 'New Description',
            'price': 149.99,
            'category': self.category.id,
            'seller': self.seller.id,
            'stock': 75,
            'discount_percentage': 5.0
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Product')
        self.assertEqual(response.data['price'], '149.99')
        
        # Verify product was created in database
        self.assertTrue(Product.objects.filter(title='New Product').exists())
    
    def test_create_product_unauthenticated(self):
        """Test creating product when not authenticated"""
        product_data = {
            'title': 'New Product',
            'description': 'New Description',
            'price': 149.99,
            'category': self.category.id,
            'seller': self.seller.id,
            'stock': 75
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_product_authenticated(self):
        """Test updating product when authenticated"""
        self.client.force_authenticate(user=self.seller_user)
        
        update_data = {
            'title': 'Updated Product',
            'description': 'Updated Description',
            'price': 199.99,
            'stock': 50
        }
        
        response = self.client.put(self.product_detail_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Product')
        self.assertEqual(response.data['price'], '199.99')
        
        # Verify product was updated in database
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.title, 'Updated Product')
        self.assertEqual(updated_product.price, 199.99)
    
    def test_partial_update_product(self):
        """Test partial update of product"""
        self.client.force_authenticate(user=self.seller_user)
        
        update_data = {
            'price': 299.99
        }
        
        response = self.client.patch(self.product_detail_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], '299.99')
        self.assertEqual(response.data['title'], 'Test Product')  # Should remain unchanged
        
        # Verify partial update in database
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.price, 299.99)
        self.assertEqual(updated_product.title, 'Test Product')
    
    def test_delete_product_authenticated(self):
        """Test deleting product when authenticated"""
        self.client.force_authenticate(user=self.seller_user)
        
        response = self.client.delete(self.product_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify product was deleted from database
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
    
    def test_delete_product_unauthenticated(self):
        """Test deleting product when not authenticated"""
        response = self.client.delete(self.product_detail_url)
        
        # Should return 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify product still exists
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())
    
    def test_product_image_upload(self):
        """Test product image upload"""
        self.client.force_authenticate(user=self.seller_user)
        
        # Create a simple image file
        image_content = b'fake image content'
        image_file = SimpleUploadedFile(
            'test_image.jpg',
            image_content,
            content_type='image/jpeg'
        )
        
        product_data = {
            'title': 'Product with Image',
            'description': 'Product with image description',
            'price': 99.99,
            'category': self.category.id,
            'seller': self.seller.id,
            'stock': 50,
            'image': image_file
        }
        
        response = self.client.post(self.products_url, product_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)
    
    def test_product_validation(self):
        """Test product validation"""
        self.client.force_authenticate(user=self.seller_user)
        
        invalid_data = {
            'title': '',  # Empty title
            'price': -10.0,  # Negative price
            'stock': -5,  # Negative stock
            'category': 99999,  # Non-existent category
            'seller': 99999,  # Non-existent seller
        }
        
        response = self.client.post(self.products_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('price', response.data)
        self.assertIn('stock', response.data)
    
    def test_product_search(self):
        """Test product search functionality"""
        # Create products with searchable content
        Product.objects.create(
            title='iPhone 13',
            description='Latest iPhone with advanced features',
            price=999.99,
            category=self.category,
            seller=self.seller,
            stock=10
        )
        
        Product.objects.create(
            title='Samsung Galaxy',
            description='Android smartphone with great camera',
            price=799.99,
            category=self.category,
            seller=self.seller,
            stock=15
        )
        
        # Search for iPhone
        response = self.client.get(f'{self.products_url}?search=iPhone')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'iPhone 13')
        
        # Search for smartphone
        response = self.client.get(f'{self.products_url}?search=smartphone')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Samsung Galaxy')
    
    def test_featured_products_filter(self):
        """Test filtering featured products"""
        # Create featured products
        Product.objects.create(
            title='Featured Product 1',
            description='Featured Description 1',
            price=99.99,
            category=self.category,
            seller=self.seller,
            stock=50,
            featured_product=True
        )
        
        Product.objects.create(
            title='Featured Product 2',
            description='Featured Description 2',
            price=149.99,
            category=self.category,
            seller=self.seller,
            stock=30,
            featured_product=True
        )
        
        # Filter featured products
        response = self.client.get(f'{self.products_url}?featured_product=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        for product in response.data['results']:
            self.assertTrue(product['featured_product'])
    
    def test_flash_sale_products_filter(self):
        """Test filtering flash sale products"""
        # Create flash sale products
        Product.objects.create(
            title='Flash Sale Product 1',
            description='Flash Sale Description 1',
            price=99.99,
            category=self.category,
            seller=self.seller,
            stock=50,
            flash_sale=True
        )
        
        # Filter flash sale products
        response = self.client.get(f'{self.products_url}?flash_sale=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['flash_sale'])
    
    def test_best_seller_products_filter(self):
        """Test filtering best seller products"""
        # Create best seller products
        Product.objects.create(
            title='Best Seller Product 1',
            description='Best Seller Description 1',
            price=199.99,
            category=self.category,
            seller=self.seller,
            stock=100,
            best_seller_product=True
        )
        
        # Filter best seller products
        response = self.client.get(f'{self.products_url}?best_seller_product=true')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['best_seller_product'])
