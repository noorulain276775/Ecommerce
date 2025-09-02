"""
Management command to rebuild search index

This command rebuilds the search index for all products.
"""

from django.core.management.base import BaseCommand
from django.contrib.postgres.search import SearchVector
from django.db import transaction

from search.models import ProductSearchIndex
from products.models import Product


class Command(BaseCommand):
    help = 'Rebuild the search index for all products'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of products to process in each batch'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing search index before rebuilding'
        )
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        clear_existing = options['clear_existing']
        
        self.stdout.write('Starting search index rebuild...')
        
        if clear_existing:
            self.stdout.write('Clearing existing search index...')
            ProductSearchIndex.objects.all().delete()
        
        # Get total count
        total_products = Product.objects.count()
        self.stdout.write(f'Processing {total_products} products...')
        
        processed = 0
        created = 0
        updated = 0
        
        # Process products in batches
        for batch_start in range(0, total_products, batch_size):
            batch_end = min(batch_start + batch_size, total_products)
            
            with transaction.atomic():
                products = Product.objects.select_related(
                    'category', 'seller'
                ).prefetch_related('tags')[batch_start:batch_end]
                
                for product in products:
                    search_index, created_flag = ProductSearchIndex.objects.get_or_create(
                        product=product,
                        defaults={
                            'search_title': product.title,
                            'search_description': product.description or '',
                            'search_category': product.category.name if product.category else '',
                            'search_seller': product.seller.name if product.seller else '',
                            'search_tags': ', '.join([tag.name for tag in product.tags.all()]) if hasattr(product, 'tags') else '',
                            'price': product.price,
                            'rating': product.rating,
                            'stock': product.stock,
                            'is_featured': product.featured_product,
                            'is_best_seller': product.best_seller_product,
                            'is_flash_sale': product.flash_sale,
                            'is_available': product.stock > 0
                        }
                    )
                    
                    if not created_flag:
                        # Update existing index
                        search_index.search_title = product.title
                        search_index.search_description = product.description or ''
                        search_index.search_category = product.category.name if product.category else ''
                        search_index.search_seller = product.seller.name if product.seller else ''
                        search_index.search_tags = ', '.join([tag.name for tag in product.tags.all()]) if hasattr(product, 'tags') else ''
                        search_index.price = product.price
                        search_index.rating = product.rating
                        search_index.stock = product.stock
                        search_index.is_featured = product.featured_product
                        search_index.is_best_seller = product.best_seller_product
                        search_index.is_flash_sale = product.flash_sale
                        search_index.is_available = product.stock > 0
                        search_index.save()
                        updated += 1
                    else:
                        created += 1
                    
                    # Update search vector
                    search_index.search_vector = SearchVector(
                        'search_title', weight='A'
                    ) + SearchVector(
                        'search_description', weight='B'
                    ) + SearchVector(
                        'search_category', weight='C'
                    ) + SearchVector(
                        'search_seller', weight='C'
                    ) + SearchVector(
                        'search_tags', weight='D'
                    )
                    search_index.save()
                    
                    processed += 1
            
            # Progress update
            progress = (processed / total_products) * 100
            self.stdout.write(
                f'Processed {processed}/{total_products} products ({progress:.1f}%)'
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Search index rebuild completed! '
                f'Created: {created}, Updated: {updated}, Total: {processed}'
            )
        )
