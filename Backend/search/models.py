"""
Search Models

This module contains models for advanced search functionality,
search analytics, and search suggestions.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

from products.models import Product, Category, Seller

User = get_user_model()


class SearchQuery(models.Model):
    """Model to track search queries for analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    query = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Search filters applied
    category_filter = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    seller_filter = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True)
    rating_filter = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    
    # Search results
    results_count = models.PositiveIntegerField(default=0)
    has_results = models.BooleanField(default=False)
    
    # Analytics
    clicked_results = models.PositiveIntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_searched = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_searched']
        indexes = [
            models.Index(fields=['query', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['has_results', 'created_at']),
        ]
    
    def __str__(self):
        return f"Search: {self.query} ({self.results_count} results)"


class SearchSuggestion(models.Model):
    """Model for search suggestions and autocomplete"""
    
    SUGGESTION_TYPE_CHOICES = [
        ('POPULAR', 'Popular Search'),
        ('TRENDING', 'Trending Search'),
        ('CATEGORY', 'Category Suggestion'),
        ('PRODUCT', 'Product Suggestion'),
        ('BRAND', 'Brand Suggestion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suggestion = models.CharField(max_length=255, unique=True)
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPE_CHOICES)
    
    # Related objects
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True, blank=True)
    
    # Analytics
    search_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    conversion_count = models.PositiveIntegerField(default=0)
    
    # Ranking and visibility
    priority = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-search_count']
        indexes = [
            models.Index(fields=['suggestion_type', 'is_active']),
            models.Index(fields=['priority', 'search_count']),
            models.Index(fields=['suggestion']),
        ]
    
    def __str__(self):
        return f"{self.suggestion} ({self.suggestion_type})"


class SearchFilter(models.Model):
    """Model for managing search filters and their configurations"""
    
    FILTER_TYPE_CHOICES = [
        ('CATEGORY', 'Category Filter'),
        ('PRICE_RANGE', 'Price Range Filter'),
        ('SELLER', 'Seller Filter'),
        ('RATING', 'Rating Filter'),
        ('BRAND', 'Brand Filter'),
        ('AVAILABILITY', 'Availability Filter'),
        ('FEATURES', 'Product Features Filter'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filter_type = models.CharField(max_length=20, choices=FILTER_TYPE_CHOICES)
    filter_name = models.CharField(max_length=100)
    filter_key = models.CharField(max_length=50, unique=True)
    
    # Filter configuration
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    # Filter options (JSON field for flexible configuration)
    filter_options = models.JSONField(default=dict)
    
    # Analytics
    usage_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'filter_name']
        indexes = [
            models.Index(fields=['filter_type', 'is_active']),
            models.Index(fields=['display_order']),
        ]
    
    def __str__(self):
        return f"{self.filter_name} ({self.filter_type})"


class SearchAnalytics(models.Model):
    """Model for comprehensive search analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(default=timezone.now)
    
    # Search metrics
    total_searches = models.PositiveIntegerField(default=0)
    unique_searches = models.PositiveIntegerField(default=0)
    searches_with_results = models.PositiveIntegerField(default=0)
    searches_without_results = models.PositiveIntegerField(default=0)
    
    # User engagement
    total_clicks = models.PositiveIntegerField(default=0)
    total_conversions = models.PositiveIntegerField(default=0)
    average_results_per_search = models.FloatField(default=0.0)
    
    # Performance metrics
    average_search_time = models.FloatField(default=0.0)  # in milliseconds
    cache_hit_rate = models.FloatField(default=0.0)
    
    # Popular searches
    top_queries = models.JSONField(default=list)
    top_categories = models.JSONField(default=list)
    top_sellers = models.JSONField(default=list)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Search Analytics - {self.date}"


class ProductSearchIndex(models.Model):
    """Model for optimized product search indexing"""
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='search_index')
    
    # Search vectors for full-text search
    search_vector = SearchVectorField(null=True, blank=True)
    
    # Precomputed search fields
    search_title = models.CharField(max_length=500, db_index=True)
    search_description = models.TextField()
    search_category = models.CharField(max_length=200, db_index=True)
    search_seller = models.CharField(max_length=200, db_index=True)
    search_tags = models.TextField(blank=True)  # Comma-separated tags
    
    # Numeric fields for filtering
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    rating = models.FloatField(null=True, blank=True, db_index=True)
    stock = models.PositiveIntegerField(db_index=True)
    
    # Boolean flags for filtering
    is_featured = models.BooleanField(default=False, db_index=True)
    is_best_seller = models.BooleanField(default=False, db_index=True)
    is_flash_sale = models.BooleanField(default=False, db_index=True)
    is_available = models.BooleanField(default=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['price', 'rating']),
            models.Index(fields=['search_category', 'search_seller']),
            models.Index(fields=['is_featured', 'is_best_seller']),
        ]
    
    def __str__(self):
        return f"Search Index: {self.product.title}"


class SearchSession(models.Model):
    """Model to track user search sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Session data
    search_queries = models.JSONField(default=list)
    applied_filters = models.JSONField(default=dict)
    viewed_products = models.JSONField(default=list)
    clicked_products = models.JSONField(default=list)
    
    # Session analytics
    total_searches = models.PositiveIntegerField(default=0)
    total_clicks = models.PositiveIntegerField(default=0)
    session_duration = models.DurationField(null=True, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'started_at']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"Search Session: {self.session_id}"


class SearchClick(models.Model):
    """Model to track search result clicks"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='clicks')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(SearchSession, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Click details
    click_position = models.PositiveIntegerField()  # Position in search results
    result_page = models.PositiveIntegerField(default=1)
    
    # Conversion tracking
    led_to_purchase = models.BooleanField(default=False)
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['search_query', 'clicked_at']),
            models.Index(fields=['product', 'clicked_at']),
            models.Index(fields=['user', 'clicked_at']),
        ]
    
    def __str__(self):
        return f"Click: {self.product.title} from '{self.search_query.query}'"
