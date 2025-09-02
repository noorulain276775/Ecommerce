"""
Management command to populate search suggestions

This command populates search suggestions from existing data.
"""

from django.core.management.base import BaseCommand
from django.db.models import Count

from search.models import SearchSuggestion
from products.models import Product, Category, Seller
from search.models import SearchQuery


class Command(BaseCommand):
    help = 'Populate search suggestions from existing data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing suggestions before populating'
        )
        parser.add_argument(
            '--min-search-count',
            type=int,
            default=5,
            help='Minimum search count for popular suggestions'
        )
    
    def handle(self, *args, **options):
        clear_existing = options['clear_existing']
        min_search_count = options['min_search_count']
        
        self.stdout.write('Starting search suggestions population...')
        
        if clear_existing:
            self.stdout.write('Clearing existing suggestions...')
            SearchSuggestion.objects.all().delete()
        
        created_count = 0
        
        # Create category suggestions
        self.stdout.write('Creating category suggestions...')
        categories = Category.objects.all()
        for category in categories:
            suggestion, created = SearchSuggestion.objects.get_or_create(
                suggestion=category.name,
                defaults={
                    'suggestion_type': 'CATEGORY',
                    'category': category,
                    'priority': 100,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        # Create seller/brand suggestions
        self.stdout.write('Creating seller suggestions...')
        sellers = Seller.objects.all()
        for seller in sellers:
            suggestion, created = SearchSuggestion.objects.get_or_create(
                suggestion=seller.name,
                defaults={
                    'suggestion_type': 'BRAND',
                    'seller': seller,
                    'priority': 90,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        # Create product suggestions (top products)
        self.stdout.write('Creating product suggestions...')
        top_products = Product.objects.filter(
            featured_product=True
        ).order_by('-rating', '-views')[:50]
        
        for product in top_products:
            suggestion, created = SearchSuggestion.objects.get_or_create(
                suggestion=product.title,
                defaults={
                    'suggestion_type': 'PRODUCT',
                    'product': product,
                    'priority': 80,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        # Create popular search suggestions
        self.stdout.write('Creating popular search suggestions...')
        popular_searches = SearchQuery.objects.filter(
            has_results=True
        ).values('query').annotate(
            search_count=Count('query')
        ).filter(
            search_count__gte=min_search_count
        ).order_by('-search_count')[:100]
        
        for search in popular_searches:
            suggestion, created = SearchSuggestion.objects.get_or_create(
                suggestion=search['query'],
                defaults={
                    'suggestion_type': 'POPULAR',
                    'search_count': search['search_count'],
                    'priority': 70,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        # Create trending suggestions (recent popular searches)
        self.stdout.write('Creating trending suggestions...')
        from django.utils import timezone
        from datetime import timedelta
        
        recent_date = timezone.now() - timedelta(days=7)
        trending_searches = SearchQuery.objects.filter(
            has_results=True,
            created_at__gte=recent_date
        ).values('query').annotate(
            search_count=Count('query')
        ).filter(
            search_count__gte=3
        ).order_by('-search_count')[:50]
        
        for search in trending_searches:
            suggestion, created = SearchSuggestion.objects.get_or_create(
                suggestion=search['query'],
                defaults={
                    'suggestion_type': 'TRENDING',
                    'search_count': search['search_count'],
                    'priority': 60,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Search suggestions population completed! '
                f'Created: {created_count} suggestions'
            )
        )
