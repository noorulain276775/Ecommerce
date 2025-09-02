"""
Search Serializers Tests

This module contains comprehensive tests for search serializers.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
import json

from search.models import (
    SearchQuery, SearchSuggestion, SearchFilter, SearchAnalytics,
    ProductSearchIndex, SearchSession, SearchClick
)
from search.serializers import (
    SearchRequestSerializer, SearchResultSerializer, SearchSuggestionSerializer,
    SearchFilterSerializer, SearchAnalyticsSerializer, SearchQuerySerializer,
    SearchSessionSerializer, SearchClickSerializer, SearchStatsSerializer,
    AdvancedSearchSerializer, SearchRecommendationSerializer, SearchPerformanceSerializer
)
from products.models import Product, Category, Seller
from accounts.models import CustomUser

User = get_user_model()


class SearchRequestSerializerTestCase(TestCase):
    """Test cases for SearchRequestSerializer"""
    
    def test_valid_search_request(self):
        """Test valid search request serialization"""
        data = {
            'query': 'laptop',
            'category': 'Electronics',
            'price_min': 500,
            'price_max': 1500,
            'rating_min': 4.0,
            'featured': True,
            'sort_by': 'price_low',
            'page': 1,
            'page_size': 20
        }
        
        serializer = SearchRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['query'], 'laptop')
        self.assertEqual(validated_data['category'], 'Electronics')
        self.assertEqual(validated_data['price_min'], 500)
        self.assertEqual(validated_data['price_max'], 1500)
        self.assertEqual(validated_data['rating_min'], 4.0)
        self.assertTrue(validated_data['featured'])
        self.assertEqual(validated_data['sort_by'], 'price_low')
        self.assertEqual(validated_data['page'], 1)
        self.assertEqual(validated_data['page_size'], 20)
    
    def test_search_request_with_defaults(self):
        """Test search request with default values"""
        data = {'query': 'smartphone'}
        
        serializer = SearchRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['query'], 'smartphone')
        self.assertEqual(validated_data['sort_by'], 'relevance')
        self.assertEqual(validated_data['page'], 1)
        self.assertEqual(validated_data['page_size'], 20)
    
    def test_search_request_invalid_price_range(self):
        """Test search request with invalid price range"""
        data = {
            'query': 'laptop',
            'price_min': 1000,
            'price_max': 500  # Invalid: min > max
        }
        
        serializer = SearchRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_search_request_invalid_rating(self):
        """Test search request with invalid rating"""
        data = {
            'query': 'laptop',
            'rating_min': 6.0  # Invalid: > 5.0
        }
        
        serializer = SearchRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('rating_min', serializer.errors)
    
    def test_search_request_invalid_page_size(self):
        """Test search request with invalid page size"""
        data = {
            'query': 'laptop',
            'page_size': 200  # Invalid: > 100
        }
        
        serializer = SearchRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('page_size', serializer.errors)


class SearchSuggestionSerializerTestCase(TestCase):
    """Test cases for SearchSuggestionSerializer"""
    
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
            price=99.99,
            category=self.category,
            seller=self.seller,
            product_number='TEST001'
        )
    
    def test_search_suggestion_serialization(self):
        """Test search suggestion serialization"""
        suggestion = SearchSuggestion.objects.create(
            suggestion='laptop',
            suggestion_type='POPULAR',
            search_count=100,
            click_count=25,
            priority=80
        )
        
        serializer = SearchSuggestionSerializer(suggestion)
        data = serializer.data
        
        self.assertEqual(data['suggestion'], 'laptop')
        self.assertEqual(data['suggestion_type'], 'POPULAR')
        self.assertEqual(data['search_count'], 100)
        self.assertEqual(data['click_count'], 25)
        self.assertEqual(data['priority'], 80)
    
    def test_search_suggestion_with_related_objects(self):
        """Test search suggestion serialization with related objects"""
        suggestion = SearchSuggestion.objects.create(
            suggestion='Electronics',
            suggestion_type='CATEGORY',
            category=self.category,
            priority=100
        )
        
        serializer = SearchSuggestionSerializer(suggestion)
        data = serializer.data
        
        self.assertEqual(data['suggestion'], 'Electronics')
        self.assertEqual(data['suggestion_type'], 'CATEGORY')
        self.assertEqual(data['category'], self.category.id)
        self.assertEqual(data['priority'], 100)


class SearchFilterSerializerTestCase(TestCase):
    """Test cases for SearchFilterSerializer"""
    
    def test_search_filter_serialization(self):
        """Test search filter serialization"""
        filter_obj = SearchFilter.objects.create(
            filter_type='CATEGORY',
            filter_name='Category Filter',
            filter_key='category',
            is_active=True,
            is_required=False,
            display_order=1,
            filter_options={'type': 'select', 'multiple': True}
        )
        
        serializer = SearchFilterSerializer(filter_obj)
        data = serializer.data
        
        self.assertEqual(data['filter_type'], 'CATEGORY')
        self.assertEqual(data['filter_name'], 'Category Filter')
        self.assertEqual(data['filter_key'], 'category')
        self.assertTrue(data['is_active'])
        self.assertFalse(data['is_required'])
        self.assertEqual(data['display_order'], 1)
        self.assertEqual(data['filter_options']['type'], 'select')


class SearchAnalyticsSerializerTestCase(TestCase):
    """Test cases for SearchAnalyticsSerializer"""
    
    def test_search_analytics_serialization(self):
        """Test search analytics serialization"""
        analytics = SearchAnalytics.objects.create(
            date='2024-01-01',
            total_searches=1000,
            unique_searches=800,
            searches_with_results=750,
            searches_without_results=250,
            total_clicks=300,
            total_conversions=50,
            average_results_per_search=8.5,
            average_search_time=250.0,
            cache_hit_rate=0.85,
            top_queries=['laptop', 'smartphone', 'tablet'],
            top_categories=['Electronics', 'Books', 'Clothing'],
            top_sellers=['Seller A', 'Seller B', 'Seller C']
        )
        
        serializer = SearchAnalyticsSerializer(analytics)
        data = serializer.data
        
        self.assertEqual(data['total_searches'], 1000)
        self.assertEqual(data['unique_searches'], 800)
        self.assertEqual(data['searches_with_results'], 750)
        self.assertEqual(data['searches_without_results'], 250)
        self.assertEqual(data['total_clicks'], 300)
        self.assertEqual(data['total_conversions'], 50)
        self.assertEqual(data['average_results_per_search'], 8.5)
        self.assertEqual(data['average_search_time'], 250.0)
        self.assertEqual(data['cache_hit_rate'], 0.85)
        self.assertEqual(data['top_queries'], ['laptop', 'smartphone', 'tablet'])
        self.assertEqual(data['top_categories'], ['Electronics', 'Books', 'Clothing'])
        self.assertEqual(data['top_sellers'], ['Seller A', 'Seller B', 'Seller C'])


class SearchQuerySerializerTestCase(TestCase):
    """Test cases for SearchQuerySerializer"""
    
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
    
    def test_search_query_serialization(self):
        """Test search query serialization"""
        search_query = SearchQuery.objects.create(
            query='laptop',
            user=self.user,
            category_filter=self.category,
            price_min=Decimal('500.00'),
            price_max=Decimal('1500.00'),
            seller_filter=self.seller,
            rating_filter=4.0,
            results_count=10,
            has_results=True,
            clicked_results=3,
            conversion_rate=30.0
        )
        
        serializer = SearchQuerySerializer(search_query)
        data = serializer.data
        
        self.assertEqual(data['query'], 'laptop')
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['category_filter'], self.category.id)
        self.assertEqual(data['price_min'], '500.00')
        self.assertEqual(data['price_max'], '1500.00')
        self.assertEqual(data['seller_filter'], self.seller.id)
        self.assertEqual(data['rating_filter'], 4.0)
        self.assertEqual(data['results_count'], 10)
        self.assertTrue(data['has_results'])
        self.assertEqual(data['clicked_results'], 3)
        self.assertEqual(data['conversion_rate'], 30.0)


class SearchSessionSerializerTestCase(TestCase):
    """Test cases for SearchSessionSerializer"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            phone='923001234567',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='customer'
        )
    
    def test_search_session_serialization(self):
        """Test search session serialization"""
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
        
        serializer = SearchSessionSerializer(session)
        data = serializer.data
        
        self.assertEqual(data['session_id'], 'test_session_123')
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['search_queries'], ['laptop', 'smartphone'])
        self.assertEqual(data['applied_filters'], {'category': 'Electronics', 'price_max': 1000})
        self.assertEqual(data['viewed_products'], [1, 2, 3])
        self.assertEqual(data['clicked_products'], [1, 2])
        self.assertEqual(data['total_searches'], 2)
        self.assertEqual(data['total_clicks'], 2)


class SearchClickSerializerTestCase(TestCase):
    """Test cases for SearchClickSerializer"""
    
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
            product_number='TEST001'
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
    
    def test_search_click_serialization(self):
        """Test search click serialization"""
        click = SearchClick.objects.create(
            search_query=self.search_query,
            product=self.product,
            user=self.user,
            session=self.search_session,
            click_position=3,
            result_page=1,
            led_to_purchase=False
        )
        
        serializer = SearchClickSerializer(click)
        data = serializer.data
        
        self.assertEqual(data['search_query'], self.search_query.id)
        self.assertEqual(data['product'], self.product.id)
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['session'], self.search_session.id)
        self.assertEqual(data['click_position'], 3)
        self.assertEqual(data['result_page'], 1)
        self.assertFalse(data['led_to_purchase'])
        self.assertEqual(data['product_title'], 'Test Product')
        self.assertEqual(data['search_query_text'], 'laptop')
    
    def test_search_click_creation(self):
        """Test search click creation"""
        data = {
            'search_query': self.search_query.id,
            'product': self.product.id,
            'click_position': 2,
            'result_page': 1,
            'led_to_purchase': True,
            'purchase_amount': '99.99'
        }
        
        serializer = SearchClickSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        click = serializer.save()
        self.assertEqual(click.search_query, self.search_query)
        self.assertEqual(click.product, self.product)
        self.assertEqual(click.click_position, 2)
        self.assertTrue(click.led_to_purchase)
        self.assertEqual(click.purchase_amount, Decimal('99.99'))


class AdvancedSearchSerializerTestCase(TestCase):
    """Test cases for AdvancedSearchSerializer"""
    
    def test_advanced_search_valid_data(self):
        """Test advanced search with valid data"""
        data = {
            'query': 'laptop',
            'search_fields': ['title', 'description'],
            'must_contain': ['gaming', 'performance'],
            'should_contain': ['portable', 'lightweight'],
            'must_not_contain': ['cheap', 'budget'],
            'fuzzy_search': True,
            'fuzzy_threshold': 0.8,
            'proximity_search': True,
            'proximity_distance': 5,
            'wildcard_search': False,
            'exact_phrase': 'gaming laptop'
        }
        
        serializer = AdvancedSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['query'], 'laptop')
        self.assertEqual(validated_data['search_fields'], ['title', 'description'])
        self.assertEqual(validated_data['must_contain'], ['gaming', 'performance'])
        self.assertEqual(validated_data['should_contain'], ['portable', 'lightweight'])
        self.assertEqual(validated_data['must_not_contain'], ['cheap', 'budget'])
        self.assertTrue(validated_data['fuzzy_search'])
        self.assertEqual(validated_data['fuzzy_threshold'], 0.8)
        self.assertTrue(validated_data['proximity_search'])
        self.assertEqual(validated_data['proximity_distance'], 5)
        self.assertFalse(validated_data['wildcard_search'])
        self.assertEqual(validated_data['exact_phrase'], 'gaming laptop')
    
    def test_advanced_search_with_exact_phrase_only(self):
        """Test advanced search with exact phrase only"""
        data = {
            'exact_phrase': 'gaming laptop'
        }
        
        serializer = AdvancedSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['exact_phrase'], 'gaming laptop')
    
    def test_advanced_search_no_query_or_phrase(self):
        """Test advanced search with no query or phrase"""
        data = {
            'search_fields': ['title', 'description']
        }
        
        serializer = AdvancedSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_advanced_search_invalid_fuzzy_threshold(self):
        """Test advanced search with invalid fuzzy threshold"""
        data = {
            'query': 'laptop',
            'fuzzy_threshold': 1.5  # Invalid: > 1.0
        }
        
        serializer = AdvancedSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('fuzzy_threshold', serializer.errors)
    
    def test_advanced_search_invalid_proximity_distance(self):
        """Test advanced search with invalid proximity distance"""
        data = {
            'query': 'laptop',
            'proximity_distance': 25  # Invalid: > 20
        }
        
        serializer = AdvancedSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('proximity_distance', serializer.errors)


class SearchStatsSerializerTestCase(TestCase):
    """Test cases for SearchStatsSerializer"""
    
    def test_search_stats_serialization(self):
        """Test search stats serialization"""
        data = {
            'total_searches': 1000,
            'unique_queries': 800,
            'average_results_per_search': 8.5,
            'top_searches': ['laptop', 'smartphone', 'tablet'],
            'search_trends': {
                '2024-01-01': {'total_searches': 100, 'unique_searches': 80},
                '2024-01-02': {'total_searches': 120, 'unique_searches': 95}
            },
            'filter_usage': {
                'category': 500,
                'price_range': 300,
                'rating': 200
            },
            'conversion_rates': {
                'overall': 15.5,
                'category': 18.2,
                'price_range': 12.8
            }
        }
        
        serializer = SearchStatsSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['total_searches'], 1000)
        self.assertEqual(validated_data['unique_queries'], 800)
        self.assertEqual(validated_data['average_results_per_search'], 8.5)
        self.assertEqual(validated_data['top_searches'], ['laptop', 'smartphone', 'tablet'])
        self.assertEqual(validated_data['search_trends']['2024-01-01']['total_searches'], 100)
        self.assertEqual(validated_data['filter_usage']['category'], 500)
        self.assertEqual(validated_data['conversion_rates']['overall'], 15.5)


class SearchRecommendationSerializerTestCase(TestCase):
    """Test cases for SearchRecommendationSerializer"""
    
    def test_search_recommendation_serialization(self):
        """Test search recommendation serialization"""
        data = {
            'query': 'laptop',
            'recommendations': [
                {'product': 'Gaming Laptop', 'score': 0.95},
                {'product': 'Business Laptop', 'score': 0.87},
                {'product': 'Student Laptop', 'score': 0.82}
            ],
            'recommendation_type': 'collaborative_filtering',
            'confidence_score': 0.88,
            'reasoning': 'Based on similar user preferences and purchase history'
        }
        
        serializer = SearchRecommendationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['query'], 'laptop')
        self.assertEqual(len(validated_data['recommendations']), 3)
        self.assertEqual(validated_data['recommendation_type'], 'collaborative_filtering')
        self.assertEqual(validated_data['confidence_score'], 0.88)
        self.assertEqual(validated_data['reasoning'], 'Based on similar user preferences and purchase history')


class SearchPerformanceSerializerTestCase(TestCase):
    """Test cases for SearchPerformanceSerializer"""
    
    def test_search_performance_serialization(self):
        """Test search performance serialization"""
        data = {
            'query': 'laptop',
            'execution_time': 150.5,
            'results_count': 25,
            'cache_hit': True,
            'database_queries': 3,
            'memory_usage': 45.2,
            'cpu_usage': 12.8
        }
        
        serializer = SearchPerformanceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertEqual(validated_data['query'], 'laptop')
        self.assertEqual(validated_data['execution_time'], 150.5)
        self.assertEqual(validated_data['results_count'], 25)
        self.assertTrue(validated_data['cache_hit'])
        self.assertEqual(validated_data['database_queries'], 3)
        self.assertEqual(validated_data['memory_usage'], 45.2)
        self.assertEqual(validated_data['cpu_usage'], 12.8)
