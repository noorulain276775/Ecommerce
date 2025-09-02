"""
Search Views Tests

This module contains comprehensive tests for search views.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
from decimal import Decimal
import json

from search.models import (
    SearchQuery, SearchSuggestion, SearchFilter, SearchAnalytics,
    ProductSearchIndex, SearchSession, SearchClick
)
from products.models import Product, Category, Seller
from accounts.models import CustomUser

User = get_user_model()


class AdvancedSearchViewTestCase(APITestCase):
    """Test cases for AdvancedSearchView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='923001234567',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='customer'
        )
        
        self.category = Category.objects.create(
            name='Electronics'
        )
        
        self.seller = Seller.objects.create(
            name='Test Seller',
            description='Test Seller Description'
        )
        
        self.product1 = Product.objects.create(
            title='Laptop Computer',
            description='High-performance laptop for work and gaming',
            price=Decimal('999.99'),
            category=self.category,
            seller=self.seller,
            stock=50,
            rating=4.5,
            featured_product=True
        )
        
        self.product2 = Product.objects.create(
            title='Smartphone',
            description='Latest smartphone with advanced features',
            price=Decimal('699.99'),
            category=self.category,
            seller=self.seller,
            product_number='TEST001',
            rating=4.2,
            best_seller_product=True
        )
        
        self.product3 = Product.objects.create(
            title='Tablet',
            description='Portable tablet for entertainment',
            price=Decimal('399.99'),
            category=self.category,
            seller=self.seller,
            stock=25,
            rating=4.0,
            flash_sale=True
        )
        
        # Create search indexes
        ProductSearchIndex.objects.create(
            product=self.product1,
            search_title='Laptop Computer',
            search_description='High-performance laptop for work and gaming',
            search_category='Electronics',
            search_seller='Test Seller',
            price=Decimal('999.99'),
            rating=4.5,
            stock=50,
            is_featured=True
        )
        
        ProductSearchIndex.objects.create(
            product=self.product2,
            search_title='Smartphone',
            search_description='Latest smartphone with advanced features',
            search_category='Electronics',
            search_seller='Test Seller',
            price=Decimal('699.99'),
            rating=4.2,
            product_number='TEST001',
            is_best_seller=True
        )
        
        ProductSearchIndex.objects.create(
            product=self.product3,
            search_title='Tablet',
            search_description='Portable tablet for entertainment',
            search_category='Electronics',
            search_seller='Test Seller',
            price=Decimal('399.99'),
            rating=4.0,
            stock=25,
            is_flash_sale=True
        )
        
        # Clear cache
        cache.clear()
    
    def test_basic_search(self):
        """Test basic search functionality"""
        url = '/api/search/'
        response = self.client.get(url, {'query': 'laptop'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
        self.assertIn('total_results', response.data)
        self.assertIn('search_time', response.data)
        
        # Should find the laptop product
        products = response.data['products']
        self.assertGreater(len(products), 0)
        
        # Check if laptop is in results
        laptop_found = any('laptop' in product['title'].lower() for product in products)
        self.assertTrue(laptop_found)
    
    def test_search_with_filters(self):
        """Test search with filters"""
        url = '/api/search/'
        params = {
            'query': 'electronics',
            'price_max': 500,
            'featured': True
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return products under $500 and featured
        products = response.data['products']
        for product in products:
            self.assertLessEqual(product['price'], 500)
    
    def test_search_with_category_filter(self):
        """Test search with category filter"""
        url = '/api/search/'
        params = {
            'category': 'Electronics'
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return all electronics products
        products = response.data['products']
        self.assertEqual(len(products), 3)  # All 3 products are electronics
    
    def test_search_with_price_range(self):
        """Test search with price range filter"""
        url = '/api/search/'
        params = {
            'price_min': 400,
            'price_max': 800
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return products in price range
        products = response.data['products']
        for product in products:
            self.assertGreaterEqual(product['price'], 400)
            self.assertLessEqual(product['price'], 800)
    
    def test_search_with_rating_filter(self):
        """Test search with rating filter"""
        url = '/api/search/'
        params = {
            'rating_min': 4.3
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return products with rating >= 4.3
        products = response.data['products']
        for product in products:
            if product.get('rating'):
                self.assertGreaterEqual(product['rating'], 4.3)
    
    def test_search_with_boolean_filters(self):
        """Test search with boolean filters"""
        url = '/api/search/'
        params = {
            'featured': True
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return only featured products
        products = response.data['products']
        for product in products:
            self.assertTrue(product.get('featured_product', False))
    
    def test_search_sorting(self):
        """Test search with different sorting options"""
        url = '/api/search/'
        
        # Test price low to high
        params = {'sort_by': 'price_low'}
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        products = response.data['products']
        if len(products) > 1:
            for i in range(len(products) - 1):
                self.assertLessEqual(products[i]['price'], products[i + 1]['price'])
        
        # Test price high to low
        params = {'sort_by': 'price_high'}
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        products = response.data['products']
        if len(products) > 1:
            for i in range(len(products) - 1):
                self.assertGreaterEqual(products[i]['price'], products[i + 1]['price'])
    
    def test_search_pagination(self):
        """Test search pagination"""
        url = '/api/search/'
        params = {
            'page': 1,
            'page_size': 2
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('page', response.data)
        self.assertIn('page_size', response.data)
        self.assertIn('total_pages', response.data)
        
        self.assertEqual(response.data['page'], 1)
        self.assertEqual(response.data['page_size'], 2)
        self.assertLessEqual(len(response.data['products']), 2)
    
    def test_search_with_no_results(self):
        """Test search with no results"""
        url = '/api/search/'
        params = {'query': 'nonexistentproduct'}
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_results'], 0)
        self.assertEqual(len(response.data['products']), 0)
    
    def test_search_creates_search_query(self):
        """Test that search creates SearchQuery record"""
        initial_count = SearchQuery.objects.count()
        
        url = '/api/search/'
        response = self.client.get(url, {'query': 'test search'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should create a SearchQuery record
        self.assertEqual(SearchQuery.objects.count(), initial_count + 1)
        
        search_query = SearchQuery.objects.filter(query='test search').first()
        self.assertIsNotNone(search_query)
        self.assertEqual(search_query.results_count, response.data['total_results'])
    
    def test_search_with_authenticated_user(self):
        """Test search with authenticated user"""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/search/'
        response = self.client.get(url, {'query': 'laptop'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should create SearchQuery with user
        search_query = SearchQuery.objects.filter(query='laptop').first()
        self.assertIsNotNone(search_query)
        self.assertEqual(search_query.user, self.user)
    
    def test_search_invalid_parameters(self):
        """Test search with invalid parameters"""
        url = '/api/search/'
        params = {
            'price_min': 1000,
            'price_max': 500  # Invalid: min > max
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_caching(self):
        """Test search result caching"""
        url = '/api/search/'
        params = {'query': 'laptop'}
        
        # First request
        response1 = self.client.get(url, params)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertFalse(response1.data.get('cache_hit', False))
        
        # Second request (should be cached)
        response2 = self.client.get(url, params)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        # Note: Cache might not be hit immediately in tests


class SearchSuggestionsViewTestCase(APITestCase):
    """Test cases for SearchSuggestionsView"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='Electronics'
        )
        
        self.seller = Seller.objects.create(
            name='Test Seller',
            description='Test Seller Description'
        )
        
        # Create search suggestions
        SearchSuggestion.objects.create(
            suggestion='laptop',
            suggestion_type='POPULAR',
            search_count=100,
            priority=100
        )
        
        SearchSuggestion.objects.create(
            suggestion='Electronics',
            suggestion_type='CATEGORY',
            category=self.category,
            priority=90
        )
        
        SearchSuggestion.objects.create(
            suggestion='Test Seller',
            suggestion_type='BRAND',
            seller=self.seller,
            priority=80
        )
    
    def test_get_suggestions_with_query(self):
        """Test getting suggestions with query"""
        url = '/api/search/suggestions/'
        response = self.client.get(url, {'q': 'lap'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions', response.data)
        
        suggestions = response.data['suggestions']
        self.assertGreater(len(suggestions), 0)
        
        # Should find laptop suggestion
        laptop_found = any('laptop' in suggestion['text'].lower() for suggestion in suggestions)
        self.assertTrue(laptop_found)
    
    def test_get_suggestions_short_query(self):
        """Test getting suggestions with short query"""
        url = '/api/search/suggestions/'
        response = self.client.get(url, {'q': 'a'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 0)
    
    def test_get_suggestions_with_limit(self):
        """Test getting suggestions with limit"""
        url = '/api/search/suggestions/'
        response = self.client.get(url, {'q': 'e', 'limit': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['suggestions']), 2)
    
    def test_get_suggestions_no_query(self):
        """Test getting suggestions without query"""
        url = '/api/search/suggestions/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['suggestions']), 0)


class SearchAnalyticsViewTestCase(APITestCase):
    """Test cases for SearchAnalyticsView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='923001234567',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='customer'
        )
        
        # Create search analytics data
        SearchAnalytics.objects.create(
            date='2024-01-01',
            total_searches=1000,
            unique_searches=800,
            searches_with_results=750,
            searches_without_results=250,
            total_clicks=300,
            total_conversions=50,
            average_search_time=250.0,
            cache_hit_rate=0.85
        )
        
        # Create search queries
        SearchQuery.objects.create(
            query='laptop',
            user=self.user,
            results_count=10,
            has_results=True
        )
        
        SearchQuery.objects.create(
            query='smartphone',
            user=self.user,
            results_count=5,
            has_results=True
        )
    
    def test_get_analytics_authenticated(self):
        """Test getting analytics when authenticated"""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/search/analytics/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_searches', response.data)
        self.assertIn('unique_queries', response.data)
        self.assertIn('top_searches', response.data)
        self.assertIn('search_trends', response.data)
    
    def test_get_analytics_unauthenticated(self):
        """Test getting analytics when not authenticated"""
        url = '/api/search/analytics/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_analytics_with_date_range(self):
        """Test getting analytics with date range"""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/search/analytics/'
        params = {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('analytics', response.data)


class SearchClickViewTestCase(APITestCase):
    """Test cases for SearchClickView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='923001234567',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='customer'
        )
        
        self.category = Category.objects.create(
            name='Electronics'
        )
        
        self.seller = Seller.objects.create(
            name='Test Seller',
            description='Test Seller Description'
        )
        
        self.product = Product.objects.create(
            title='Test Product',
            description='Test Description',
            price=99.99,
            category=self.category,
            seller=self.seller,
            stock=100
        )
        
        self.search_query = SearchQuery.objects.create(
            query='laptop',
            user=self.user,
            results_count=10,
            has_results=True
        )
        
        self.search_session = SearchSession.objects.create(
            session_id='test_session_123',
            user=self.user
        )
    
    def test_create_search_click(self):
        """Test creating a search click"""
        url = '/api/search/clicks/'
        data = {
            'search_query': self.search_query.id,
            'product': self.product.id,
            'click_position': 3,
            'result_page': 1,
            'led_to_purchase': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should create SearchClick record
        click = SearchClick.objects.filter(
            search_query=self.search_query,
            product=self.product
        ).first()
        self.assertIsNotNone(click)
        self.assertEqual(click.click_position, 3)
    
    def test_create_search_click_with_purchase(self):
        """Test creating a search click that led to purchase"""
        url = '/api/search/clicks/'
        data = {
            'search_query': self.search_query.id,
            'product': self.product.id,
            'click_position': 1,
            'result_page': 1,
            'led_to_purchase': True,
            'purchase_amount': '99.99'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should create SearchClick with purchase data
        click = SearchClick.objects.filter(
            search_query=self.search_query,
            product=self.product
        ).first()
        self.assertIsNotNone(click)
        self.assertTrue(click.led_to_purchase)
        self.assertEqual(click.purchase_amount, Decimal('99.99'))
    
    def test_create_search_click_invalid_data(self):
        """Test creating search click with invalid data"""
        url = '/api/search/clicks/'
        data = {
            'search_query': 'invalid_id',
            'product': self.product.id,
            'click_position': 3
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_search_click_updates_analytics(self):
        """Test that search click updates analytics"""
        initial_clicks = self.search_query.clicked_results
        
        url = '/api/search/clicks/'
        data = {
            'search_query': self.search_query.id,
            'product': self.product.id,
            'click_position': 2
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should update search query click count
        self.search_query.refresh_from_db()
        self.assertEqual(self.search_query.clicked_results, initial_clicks + 1)


class SearchPerformanceViewTestCase(APITestCase):
    """Test cases for SearchPerformanceView"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='923001234567',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='customer'
        )
    
    def test_get_performance_authenticated(self):
        """Test getting performance metrics when authenticated"""
        self.client.force_authenticate(user=self.user)
        
        url = '/api/search/performance/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('database_stats', response.data)
        self.assertIn('cache_stats', response.data)
        self.assertIn('performance_metrics', response.data)
        self.assertIn('recommendations', response.data)
    
    def test_get_performance_unauthenticated(self):
        """Test getting performance metrics when not authenticated"""
        url = '/api/search/performance/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
