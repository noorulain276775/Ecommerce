"""
Search Models Tests

This module contains comprehensive tests for search models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from search.models import (
    SearchQuery, SearchSuggestion, SearchFilter, SearchAnalytics,
    ProductSearchIndex, SearchSession, SearchClick
)
from products.models import Product, Category, Seller
from accounts.models import CustomUser

User = get_user_model()


class SearchQueryModelTestCase(TestCase):
    """Test cases for SearchQuery model"""
    
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
    
    def test_create_search_query(self):
        """Test creating a search query"""
        search_query = SearchQuery.objects.create(
            query='laptop',
            user=self.user,
            results_count=10,
            has_results=True
        )
        
        self.assertEqual(search_query.query, 'laptop')
        self.assertEqual(search_query.user, self.user)
        self.assertEqual(search_query.results_count, 10)
        self.assertTrue(search_query.has_results)
        self.assertIsNotNone(search_query.id)
    
    def test_search_query_with_filters(self):
        """Test search query with filters"""
        search_query = SearchQuery.objects.create(
            query='smartphone',
            user=self.user,
            category_filter=self.category,
            price_min=Decimal('100.00'),
            price_max=Decimal('1000.00'),
            seller_filter=self.seller,
            rating_filter=4.0,
            results_count=5,
            has_results=True
        )
        
        self.assertEqual(search_query.category_filter, self.category)
        self.assertEqual(search_query.price_min, Decimal('100.00'))
        self.assertEqual(search_query.price_max, Decimal('1000.00'))
        self.assertEqual(search_query.seller_filter, self.seller)
        self.assertEqual(search_query.rating_filter, 4.0)
    
    def test_search_query_analytics(self):
        """Test search query analytics fields"""
        search_query = SearchQuery.objects.create(
            query='tablet',
            user=self.user,
            results_count=8,
            has_results=True,
            clicked_results=3
        )
        
        # Test conversion rate calculation
        search_query.conversion_rate = (search_query.clicked_results / search_query.results_count) * 100
        search_query.save()
        
        expected_conversion_rate = (3 / 8) * 100
        self.assertEqual(search_query.conversion_rate, expected_conversion_rate)
    
    def test_search_query_string_representation(self):
        """Test search query string representation"""
        search_query = SearchQuery.objects.create(
            query='headphones',
            results_count=15,
            has_results=True
        )
        
        expected_string = "Search: headphones (15 results)"
        self.assertEqual(str(search_query), expected_string)


class SearchSuggestionModelTestCase(TestCase):
    """Test cases for SearchSuggestion model"""
    
    def setUp(self):
        """Set up test data"""
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
            product_number='TEST001',
            price=99.99,
            category=self.category,
            seller=self.seller
        )
    
    def test_create_search_suggestion(self):
        """Test creating a search suggestion"""
        suggestion = SearchSuggestion.objects.create(
            suggestion='laptop',
            suggestion_type='POPULAR',
            search_count=100,
            click_count=25,
            priority=80,
            is_active=True
        )
        
        self.assertEqual(suggestion.suggestion, 'laptop')
        self.assertEqual(suggestion.suggestion_type, 'POPULAR')
        self.assertEqual(suggestion.search_count, 100)
        self.assertEqual(suggestion.click_count, 25)
        self.assertEqual(suggestion.priority, 80)
        self.assertTrue(suggestion.is_active)
    
    def test_search_suggestion_with_related_objects(self):
        """Test search suggestion with related objects"""
        # Category suggestion
        category_suggestion = SearchSuggestion.objects.create(
            suggestion='Electronics Category',
            suggestion_type='CATEGORY',
            category=self.category,
            priority=100
        )
        
        # Product suggestion
        product_suggestion = SearchSuggestion.objects.create(
            suggestion='Test Product',
            suggestion_type='PRODUCT',
            product=self.product,
            priority=90
        )
        
        # Seller suggestion
        seller_suggestion = SearchSuggestion.objects.create(
            suggestion='Test Seller Brand',
            suggestion_type='BRAND',
            seller=self.seller,
            priority=85
        )
        
        self.assertEqual(category_suggestion.category, self.category)
        self.assertEqual(product_suggestion.product, self.product)
        self.assertEqual(seller_suggestion.seller, self.seller)
    
    def test_search_suggestion_string_representation(self):
        """Test search suggestion string representation"""
        suggestion = SearchSuggestion.objects.create(
            suggestion='smartphone',
            suggestion_type='POPULAR'
        )
        
        expected_string = "smartphone (POPULAR)"
        self.assertEqual(str(suggestion), expected_string)


class SearchFilterModelTestCase(TestCase):
    """Test cases for SearchFilter model"""
    
    def test_create_search_filter(self):
        """Test creating a search filter"""
        filter_obj = SearchFilter.objects.create(
            filter_type='CATEGORY',
            filter_name='Category Filter',
            filter_key='category',
            is_active=True,
            is_required=False,
            display_order=1,
            filter_options={'type': 'select', 'multiple': True}
        )
        
        self.assertEqual(filter_obj.filter_type, 'CATEGORY')
        self.assertEqual(filter_obj.filter_name, 'Category Filter')
        self.assertEqual(filter_obj.filter_key, 'category')
        self.assertTrue(filter_obj.is_active)
        self.assertFalse(filter_obj.is_required)
        self.assertEqual(filter_obj.display_order, 1)
        self.assertEqual(filter_obj.filter_options['type'], 'select')
    
    def test_search_filter_string_representation(self):
        """Test search filter string representation"""
        filter_obj = SearchFilter.objects.create(
            filter_type='PRICE_RANGE',
            filter_name='Price Range',
            filter_key='price_range'
        )
        
        expected_string = "Price Range (PRICE_RANGE)"
        self.assertEqual(str(filter_obj), expected_string)


class SearchAnalyticsModelTestCase(TestCase):
    """Test cases for SearchAnalytics model"""
    
    def test_create_search_analytics(self):
        """Test creating search analytics"""
        analytics = SearchAnalytics.objects.create(
            date=timezone.now().date(),
            total_searches=1000,
            unique_searches=800,
            searches_with_results=750,
            searches_without_results=250,
            total_clicks=300,
            total_conversions=50,
            average_results_per_search=8.5,
            average_search_time=250.0,
            cache_hit_rate=0.85
        )
        
        self.assertEqual(analytics.total_searches, 1000)
        self.assertEqual(analytics.unique_searches, 800)
        self.assertEqual(analytics.searches_with_results, 750)
        self.assertEqual(analytics.searches_without_results, 250)
        self.assertEqual(analytics.total_clicks, 300)
        self.assertEqual(analytics.total_conversions, 50)
        self.assertEqual(analytics.average_results_per_search, 8.5)
        self.assertEqual(analytics.average_search_time, 250.0)
        self.assertEqual(analytics.cache_hit_rate, 0.85)
    
    def test_search_analytics_with_json_fields(self):
        """Test search analytics with JSON fields"""
        analytics = SearchAnalytics.objects.create(
            date=timezone.now().date(),
            top_queries=['laptop', 'smartphone', 'tablet'],
            top_categories=['Electronics', 'Books', 'Clothing'],
            top_sellers=['Seller A', 'Seller B', 'Seller C']
        )
        
        self.assertEqual(analytics.top_queries, ['laptop', 'smartphone', 'tablet'])
        self.assertEqual(analytics.top_categories, ['Electronics', 'Books', 'Clothing'])
        self.assertEqual(analytics.top_sellers, ['Seller A', 'Seller B', 'Seller C'])
    
    def test_search_analytics_string_representation(self):
        """Test search analytics string representation"""
        today = timezone.now().date()
        analytics = SearchAnalytics.objects.create(date=today)
        
        expected_string = f"Search Analytics - {today}"
        self.assertEqual(str(analytics), expected_string)


class ProductSearchIndexModelTestCase(TestCase):
    """Test cases for ProductSearchIndex model"""
    
    def setUp(self):
        """Set up test data"""
        self.category = Category.objects.create(
            name='Electronics'
        )
        
        self.seller = Seller.objects.create(
            name='Test Seller',
            description='Test Seller Description'
        )
        
        self.product = Product.objects.create(
            title='Test Laptop',
            description='A great laptop for work and play',
            product_number='LAPTOP001',
            price=Decimal('999.99'),
            category=self.category,
            seller=self.seller,
            featured_product=True,
            best_seller_product=False,
            flash_sale=False
        )
    
    def test_create_product_search_index(self):
        """Test creating a product search index"""
        search_index = ProductSearchIndex.objects.create(
            product=self.product,
            search_title='Test Laptop',
            search_description='A great laptop for work and play',
            search_category='Electronics',
            search_seller='Test Seller',
            search_tags='laptop, computer, electronics',
            price=Decimal('999.99'),
            rating=4.5,
            stock=50,
            is_featured=True,
            is_best_seller=False,
            is_flash_sale=False,
            is_available=True
        )
        
        self.assertEqual(search_index.product, self.product)
        self.assertEqual(search_index.search_title, 'Test Laptop')
        self.assertEqual(search_index.search_description, 'A great laptop for work and play')
        self.assertEqual(search_index.search_category, 'Electronics')
        self.assertEqual(search_index.search_seller, 'Test Seller')
        self.assertEqual(search_index.search_tags, 'laptop, computer, electronics')
        self.assertEqual(search_index.price, Decimal('999.99'))
        self.assertEqual(search_index.rating, 4.5)
        self.assertEqual(search_index.stock, 50)
        self.assertTrue(search_index.is_featured)
        self.assertFalse(search_index.is_best_seller)
        self.assertFalse(search_index.is_flash_sale)
        self.assertTrue(search_index.is_available)
    
    def test_product_search_index_string_representation(self):
        """Test product search index string representation"""
        search_index = ProductSearchIndex.objects.create(
            product=self.product,
            search_title='Test Laptop',
            search_description='A great laptop',
            search_category='Electronics',
            search_seller='Test Seller',
            price=Decimal('999.99'),
            rating=4.5,
            stock=50
        )
        
        expected_string = "Search Index: Test Laptop"
        self.assertEqual(str(search_index), expected_string)


class SearchSessionModelTestCase(TestCase):
    """Test cases for SearchSession model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='923001234567',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='customer'
        )
    
    def test_create_search_session(self):
        """Test creating a search session"""
        session = SearchSession.objects.create(
            session_id='test_session_123',
            user=self.user,
            search_queries=['laptop', 'smartphone'],
            applied_filters={'category': 'Electronics', 'price_max': 1000},
            viewed_products=[1, 2, 3],
            clicked_products=[1, 2],
            total_searches=2,
            total_clicks=2
        )
        
        self.assertEqual(session.session_id, 'test_session_123')
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.search_queries, ['laptop', 'smartphone'])
        self.assertEqual(session.applied_filters, {'category': 'Electronics', 'price_max': 1000})
        self.assertEqual(session.viewed_products, [1, 2, 3])
        self.assertEqual(session.clicked_products, [1, 2])
        self.assertEqual(session.total_searches, 2)
        self.assertEqual(session.total_clicks, 2)
    
    def test_search_session_string_representation(self):
        """Test search session string representation"""
        session = SearchSession.objects.create(
            session_id='test_session_456'
        )
        
        expected_string = "Search Session: test_session_456"
        self.assertEqual(str(session), expected_string)


class SearchClickModelTestCase(TestCase):
    """Test cases for SearchClick model"""
    
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
            product_number='TEST001',
            price=99.99,
            category=self.category,
            seller=self.seller
        )
        
        self.search_query = SearchQuery.objects.create(
            query='laptop',
            user=self.user,
            results_count=10,
            has_results=True
        )
        
        self.search_session = SearchSession.objects.create(
            session_id='test_session_789',
            user=self.user
        )
    
    def test_create_search_click(self):
        """Test creating a search click"""
        click = SearchClick.objects.create(
            search_query=self.search_query,
            product=self.product,
            user=self.user,
            session=self.search_session,
            click_position=3,
            result_page=1,
            led_to_purchase=False
        )
        
        self.assertEqual(click.search_query, self.search_query)
        self.assertEqual(click.product, self.product)
        self.assertEqual(click.user, self.user)
        self.assertEqual(click.session, self.search_session)
        self.assertEqual(click.click_position, 3)
        self.assertEqual(click.result_page, 1)
        self.assertFalse(click.led_to_purchase)
    
    def test_search_click_with_purchase(self):
        """Test search click that led to purchase"""
        click = SearchClick.objects.create(
            search_query=self.search_query,
            product=self.product,
            user=self.user,
            click_position=1,
            result_page=1,
            led_to_purchase=True,
            purchase_amount=Decimal('99.99')
        )
        
        self.assertTrue(click.led_to_purchase)
        self.assertEqual(click.purchase_amount, Decimal('99.99'))
    
    def test_search_click_string_representation(self):
        """Test search click string representation"""
        click = SearchClick.objects.create(
            search_query=self.search_query,
            product=self.product,
            click_position=2
        )
        
        expected_string = "Click: Test Product from 'laptop'"
        self.assertEqual(str(click), expected_string)
