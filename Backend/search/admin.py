"""
Search Admin

This module contains admin configurations for search models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    SearchQuery, SearchSuggestion, SearchFilter, SearchAnalytics,
    ProductSearchIndex, SearchSession, SearchClick
)


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = [
        'query', 'user', 'results_count', 'has_results', 
        'clicked_results', 'conversion_rate', 'created_at'
    ]
    list_filter = [
        'has_results', 'created_at', 'category_filter', 'seller_filter'
    ]
    search_fields = ['query', 'user__phone', 'user__first_name']
    readonly_fields = [
        'id', 'results_count', 'has_results', 'clicked_results', 
        'conversion_rate', 'created_at', 'last_searched'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category_filter', 'seller_filter')


@admin.register(SearchSuggestion)
class SearchSuggestionAdmin(admin.ModelAdmin):
    list_display = [
        'suggestion', 'suggestion_type', 'priority', 'search_count', 
        'click_count', 'is_active', 'created_at'
    ]
    list_filter = [
        'suggestion_type', 'is_active', 'created_at'
    ]
    search_fields = ['suggestion']
    list_editable = ['priority', 'is_active']
    ordering = ['-priority', '-search_count']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'product', 'seller')


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = [
        'filter_name', 'filter_type', 'filter_key', 'is_active', 
        'is_required', 'display_order', 'usage_count'
    ]
    list_filter = [
        'filter_type', 'is_active', 'is_required'
    ]
    search_fields = ['filter_name', 'filter_key']
    list_editable = ['is_active', 'is_required', 'display_order']
    ordering = ['display_order', 'filter_name']


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_searches', 'unique_searches', 'searches_with_results',
        'searches_without_results', 'total_clicks', 'total_conversions',
        'average_search_time', 'cache_hit_rate'
    ]
    list_filter = ['date']
    readonly_fields = [
        'id', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def has_add_permission(self, request):
        return False  # Analytics are auto-generated


@admin.register(ProductSearchIndex)
class ProductSearchIndexAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'search_title', 'price', 'rating', 'stock',
        'is_featured', 'is_best_seller', 'is_flash_sale', 'is_available'
    ]
    list_filter = [
        'is_featured', 'is_best_seller', 'is_flash_sale', 'is_available',
        'search_category', 'search_seller'
    ]
    search_fields = [
        'search_title', 'search_description', 'search_category', 
        'search_seller', 'search_tags'
    ]
    readonly_fields = [
        'search_vector', 'created_at', 'updated_at'
    ]
    ordering = ['-updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'product__category', 'product__seller')


@admin.register(SearchSession)
class SearchSessionAdmin(admin.ModelAdmin):
    list_display = [
        'session_id', 'user', 'total_searches', 'total_clicks',
        'session_duration', 'started_at', 'last_activity'
    ]
    list_filter = [
        'started_at', 'last_activity', 'ended_at'
    ]
    search_fields = ['session_id', 'user__phone', 'user__first_name']
    readonly_fields = [
        'id', 'session_id', 'total_searches', 'total_clicks',
        'session_duration', 'started_at', 'last_activity', 'ended_at'
    ]
    date_hierarchy = 'started_at'
    ordering = ['-last_activity']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SearchClick)
class SearchClickAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'search_query', 'user', 'click_position',
        'result_page', 'led_to_purchase', 'clicked_at'
    ]
    list_filter = [
        'led_to_purchase', 'result_page', 'clicked_at'
    ]
    search_fields = [
        'product__title', 'search_query__query', 'user__phone'
    ]
    readonly_fields = [
        'id', 'clicked_at'
    ]
    date_hierarchy = 'clicked_at'
    ordering = ['-clicked_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'search_query', 'user', 'session'
        )


# Custom admin site configuration
admin.site.site_header = "E-commerce Search Administration"
admin.site.site_title = "Search Admin"
admin.site.index_title = "Search & Filtering System"
