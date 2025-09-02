"""
Search App Configuration

This module contains the configuration for the search app.
"""

from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search'
    verbose_name = 'Search & Filtering System'
    
    def ready(self):
        """Import signal handlers when the app is ready"""
        import search.signals