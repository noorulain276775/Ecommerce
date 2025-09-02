"""
Search Serializers

This module contains serializers for search functionality,
including search requests, results, and analytics.
"""

from rest_framework import serializers
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, F, Count, Avg, Max, Min
from django.core.cache import cache
from decimal import Decimal
import json

from .models import (
    SearchQuery, SearchSuggestion, SearchFilter, SearchAnalytics,
    ProductSearchIndex, SearchSession, SearchClick
)
from products.models import Product, Category, Seller
from products.serializers import ProductSerializer


class SearchRequestSerializer(serializers.Serializer):
    """Serializer for search requests"""
    
    query = serializers.CharField(max_length=255, required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    price_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    price_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    seller = serializers.CharField(required=False, allow_blank=True)
    rating_min = serializers.FloatField(required=False, allow_null=True, min_value=0.0, max_value=5.0)
    featured = serializers.BooleanField(required=False, allow_null=True)
    best_seller = serializers.BooleanField(required=False, allow_null=True)
    flash_sale = serializers.BooleanField(required=False, allow_null=True)
    in_stock = serializers.BooleanField(required=False, allow_null=True)
    
    # Sorting options
    sort_by = serializers.ChoiceField(
        choices=[
            ('relevance', 'Relevance'),
            ('price_low', 'Price: Low to High'),
            ('price_high', 'Price: High to Low'),
            ('rating', 'Rating'),
            ('newest', 'Newest'),
            ('popularity', 'Popularity'),
        ],
        default='relevance',
        required=False
    )
    
    # Pagination
    page = serializers.IntegerField(min_value=1, default=1, required=False)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20, required=False)
    
    def validate_price_range(self, data):
        """Validate price range"""
        price_min = data.get('price_min')
        price_max = data.get('price_max')
        
        if price_min is not None and price_max is not None:
            if price_min > price_max:
                raise serializers.ValidationError("Minimum price cannot be greater than maximum price.")
        
        return data


class SearchSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for search suggestions"""
    
    class Meta:
        model = SearchSuggestion
        fields = [
            'id', 'suggestion', 'suggestion_type', 'category', 'product', 'seller',
            'search_count', 'click_count', 'priority'
        ]


class SearchFilterSerializer(serializers.ModelSerializer):
    """Serializer for search filters"""
    
    class Meta:
        model = SearchFilter
        fields = [
            'id', 'filter_type', 'filter_name', 'filter_key',
            'is_active', 'is_required', 'display_order', 'filter_options'
        ]


class ProductSearchResultSerializer(serializers.ModelSerializer):
    """Serializer for product search results"""
    
    # Include product details
    product = ProductSerializer(read_only=True)
    
    # Search-specific fields
    search_rank = serializers.FloatField(read_only=True)
    matched_fields = serializers.ListField(read_only=True)
    
    class Meta:
        model = ProductSearchIndex
        fields = [
            'product', 'search_rank', 'matched_fields',
            'price', 'rating', 'stock', 'is_featured',
            'is_best_seller', 'is_flash_sale', 'is_available'
        ]


class SearchResultSerializer(serializers.Serializer):
    """Serializer for complete search results"""
    
    query = serializers.CharField()
    total_results = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    
    # Results
    products = ProductSearchResultSerializer(many=True)
    
    # Applied filters
    applied_filters = serializers.DictField()
    
    # Available filters
    available_filters = SearchFilterSerializer(many=True)
    
    # Search suggestions
    suggestions = SearchSuggestionSerializer(many=True)
    
    # Performance metrics
    search_time = serializers.FloatField()
    cache_hit = serializers.BooleanField()


class SearchAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for search analytics"""
    
    class Meta:
        model = SearchAnalytics
        fields = [
            'id', 'date', 'total_searches', 'unique_searches',
            'searches_with_results', 'searches_without_results',
            'total_clicks', 'total_conversions', 'average_results_per_search',
            'average_search_time', 'cache_hit_rate', 'top_queries',
            'top_categories', 'top_sellers', 'created_at', 'updated_at'
        ]


class SearchQuerySerializer(serializers.ModelSerializer):
    """Serializer for search queries"""
    
    class Meta:
        model = SearchQuery
        fields = [
            'id', 'query', 'user', 'session_id', 'category_filter',
            'price_min', 'price_max', 'seller_filter', 'rating_filter',
            'results_count', 'has_results', 'clicked_results',
            'conversion_rate', 'created_at', 'last_searched'
        ]
        read_only_fields = [
            'id', 'user', 'session_id', 'results_count', 'has_results',
            'clicked_results', 'conversion_rate', 'created_at', 'last_searched'
        ]


class SearchSessionSerializer(serializers.ModelSerializer):
    """Serializer for search sessions"""
    
    class Meta:
        model = SearchSession
        fields = [
            'id', 'session_id', 'user', 'search_queries', 'applied_filters',
            'viewed_products', 'clicked_products', 'total_searches',
            'total_clicks', 'session_duration', 'started_at',
            'last_activity', 'ended_at'
        ]
        read_only_fields = [
            'id', 'session_id', 'user', 'total_searches', 'total_clicks',
            'session_duration', 'started_at', 'last_activity', 'ended_at'
        ]


class SearchClickSerializer(serializers.ModelSerializer):
    """Serializer for search clicks"""
    
    product_title = serializers.CharField(source='product.title', read_only=True)
    search_query_text = serializers.CharField(source='search_query.query', read_only=True)
    
    class Meta:
        model = SearchClick
        fields = [
            'id', 'search_query', 'product', 'user', 'session',
            'click_position', 'result_page', 'led_to_purchase',
            'purchase_amount', 'clicked_at', 'product_title', 'search_query_text'
        ]
        read_only_fields = [
            'id', 'user', 'session', 'clicked_at', 'product_title', 'search_query_text'
        ]


class SearchStatsSerializer(serializers.Serializer):
    """Serializer for search statistics"""
    
    total_searches = serializers.IntegerField()
    unique_queries = serializers.IntegerField()
    average_results_per_search = serializers.FloatField()
    top_searches = serializers.ListField()
    search_trends = serializers.DictField()
    filter_usage = serializers.DictField()
    conversion_rates = serializers.DictField()


class AdvancedSearchSerializer(serializers.Serializer):
    """Serializer for advanced search with complex queries"""
    
    # Text search
    query = serializers.CharField(required=False, allow_blank=True)
    search_fields = serializers.ListField(
        child=serializers.ChoiceField(choices=['title', 'description', 'category', 'seller', 'tags']),
        required=False
    )
    
    # Boolean search
    must_contain = serializers.ListField(required=False)
    should_contain = serializers.ListField(required=False)
    must_not_contain = serializers.ListField(required=False)
    
    # Fuzzy search
    fuzzy_search = serializers.BooleanField(default=False)
    fuzzy_threshold = serializers.FloatField(default=0.7, min_value=0.0, max_value=1.0)
    
    # Proximity search
    proximity_search = serializers.BooleanField(default=False)
    proximity_distance = serializers.IntegerField(default=5, min_value=1, max_value=20)
    
    # Wildcard search
    wildcard_search = serializers.BooleanField(default=False)
    
    # Phrase search
    exact_phrase = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate advanced search parameters"""
        query = data.get('query', '')
        exact_phrase = data.get('exact_phrase', '')
        
        if not query and not exact_phrase:
            raise serializers.ValidationError("Either 'query' or 'exact_phrase' must be provided.")
        
        return data


class SearchRecommendationSerializer(serializers.Serializer):
    """Serializer for search recommendations"""
    
    query = serializers.CharField()
    recommendations = serializers.ListField()
    recommendation_type = serializers.CharField()
    confidence_score = serializers.FloatField()
    reasoning = serializers.CharField()


class SearchPerformanceSerializer(serializers.Serializer):
    """Serializer for search performance metrics"""
    
    query = serializers.CharField()
    execution_time = serializers.FloatField()
    results_count = serializers.IntegerField()
    cache_hit = serializers.BooleanField()
    database_queries = serializers.IntegerField()
    memory_usage = serializers.FloatField()
    cpu_usage = serializers.FloatField()
