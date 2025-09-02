"""
Search URLs

This module contains URL patterns for search functionality.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'search'

urlpatterns = [
    # Advanced search
    path('', views.AdvancedSearchView.as_view(), name='advanced_search'),
    
    # Search suggestions
    path('suggestions/', views.SearchSuggestionsView.as_view(), name='search_suggestions'),
    
    # Search analytics
    path('analytics/', views.SearchAnalyticsView.as_view(), name='search_analytics'),
    
    # Search click tracking
    path('clicks/', views.SearchClickView.as_view(), name='search_clicks'),
    
    # Search performance monitoring
    path('performance/', views.SearchPerformanceView.as_view(), name='search_performance'),
]