"""
Search Signals

This module contains signal handlers for search functionality.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from django.core.cache import cache

from .models import ProductSearchIndex, SearchSuggestion
from products.models import Product, Category, Seller


@receiver(post_save, sender=Product)
def update_product_search_index(sender, instance, created, **kwargs):
    """Update product search index when product is saved"""
    try:
        # Create or update search index
        search_index, created = ProductSearchIndex.objects.get_or_create(
            product=instance,
            defaults={
                'search_title': instance.title,
                'search_description': instance.description or '',
                'search_category': instance.category.name if instance.category else '',
                'search_seller': instance.seller.name if instance.seller else '',
                'search_tags': ', '.join([tag.name for tag in instance.tags.all()]) if hasattr(instance, 'tags') else '',
                'price': instance.price,
                'rating': instance.rating,
                'stock': instance.stock,
                'is_featured': instance.featured_product,
                'is_best_seller': instance.best_seller_product,
                'is_flash_sale': instance.flash_sale,
                'is_available': instance.stock > 0
            }
        )
        
        if not created:
            # Update existing index
            search_index.search_title = instance.title
            search_index.search_description = instance.description or ''
            search_index.search_category = instance.category.name if instance.category else ''
            search_index.search_seller = instance.seller.name if instance.seller else ''
            search_index.search_tags = ', '.join([tag.name for tag in instance.tags.all()]) if hasattr(instance, 'tags') else ''
            search_index.price = instance.price
            search_index.rating = instance.rating
            search_index.stock = instance.stock
            search_index.is_featured = instance.featured_product
            search_index.is_best_seller = instance.best_seller_product
            search_index.is_flash_sale = instance.flash_sale
            search_index.is_available = instance.stock > 0
            search_index.save()
        
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
        
        # Clear related caches
        cache.delete_many([
            f"product_search_{instance.id}",
            f"category_products_{instance.category.id}" if instance.category else None,
            f"seller_products_{instance.seller.id}" if instance.seller else None,
        ])
        
    except Exception as e:
        # Log error but don't fail the product save
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating search index for product {instance.id}: {e}")


@receiver(post_delete, sender=Product)
def delete_product_search_index(sender, instance, **kwargs):
    """Delete product search index when product is deleted"""
    try:
        ProductSearchIndex.objects.filter(product=instance).delete()
        
        # Clear related caches
        cache.delete_many([
            f"product_search_{instance.id}",
            f"category_products_{instance.category.id}" if instance.category else None,
            f"seller_products_{instance.seller.id}" if instance.seller else None,
        ])
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting search index for product {instance.id}: {e}")


@receiver(post_save, sender=Category)
def update_category_search_suggestions(sender, instance, created, **kwargs):
    """Update search suggestions when category is saved"""
    try:
        if created:
            # Create category suggestion
            SearchSuggestion.objects.get_or_create(
                suggestion=instance.name,
                defaults={
                    'suggestion_type': 'CATEGORY',
                    'category': instance,
                    'priority': 100
                }
            )
        else:
            # Update existing suggestion
            suggestion = SearchSuggestion.objects.filter(
                suggestion=instance.name,
                suggestion_type='CATEGORY'
            ).first()
            
            if suggestion:
                suggestion.category = instance
                suggestion.save()
                
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating search suggestions for category {instance.id}: {e}")


@receiver(post_save, sender=Seller)
def update_seller_search_suggestions(sender, instance, created, **kwargs):
    """Update search suggestions when seller is saved"""
    try:
        if created:
            # Create seller suggestion
            SearchSuggestion.objects.get_or_create(
                suggestion=instance.name,
                defaults={
                    'suggestion_type': 'BRAND',
                    'seller': instance,
                    'priority': 90
                }
            )
        else:
            # Update existing suggestion
            suggestion = SearchSuggestion.objects.filter(
                suggestion=instance.name,
                suggestion_type='BRAND'
            ).first()
            
            if suggestion:
                suggestion.seller = instance
                suggestion.save()
                
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating search suggestions for seller {instance.id}: {e}")


@receiver(post_delete, sender=Category)
def delete_category_search_suggestions(sender, instance, **kwargs):
    """Delete search suggestions when category is deleted"""
    try:
        SearchSuggestion.objects.filter(
            suggestion=instance.name,
            suggestion_type='CATEGORY'
        ).delete()
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting search suggestions for category {instance.id}: {e}")


@receiver(post_delete, sender=Seller)
def delete_seller_search_suggestions(sender, instance, **kwargs):
    """Delete search suggestions when seller is deleted"""
    try:
        SearchSuggestion.objects.filter(
            suggestion=instance.name,
            suggestion_type='BRAND'
        ).delete()
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting search suggestions for seller {instance.id}: {e}")
