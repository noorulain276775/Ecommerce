"""
Advanced caching configuration for Django E-commerce
"""
from django.core.cache import cache
from django.conf import settings
import json
import logging
from functools import wraps
from typing import Any, Optional, Callable
import hashlib

logger = logging.getLogger(__name__)

class CacheManager:
    """Advanced cache management with Redis"""
    
    # Cache key prefixes
    CACHE_PREFIXES = {
        'user': 'user',
        'product': 'product',
        'category': 'category',
        'cart': 'cart',
        'order': 'order',
        'search': 'search',
        'analytics': 'analytics',
        'session': 'session',
    }
    
    # Default cache timeouts (in seconds)
    DEFAULT_TIMEOUTS = {
        'user': 3600,  # 1 hour
        'product': 1800,  # 30 minutes
        'category': 7200,  # 2 hours
        'cart': 1800,  # 30 minutes
        'order': 3600,  # 1 hour
        'search': 900,  # 15 minutes
        'analytics': 3600,  # 1 hour
        'session': 1800,  # 30 minutes
    }
    
    @classmethod
    def get_cache_key(cls, prefix: str, identifier: str, *args) -> str:
        """Generate consistent cache key"""
        key_parts = [cls.CACHE_PREFIXES.get(prefix, prefix), str(identifier)]
        if args:
            key_parts.extend(str(arg) for arg in args)
        return ':'.join(key_parts)
    
    @classmethod
    def set(cls, key: str, value: Any, timeout: Optional[int] = None, prefix: str = None) -> bool:
        """Set cache value with optional prefix"""
        if prefix:
            key = cls.get_cache_key(prefix, key)
        
        try:
            # Serialize complex objects
            if not isinstance(value, (str, int, float, bool, list, dict)):
                value = json.dumps(value, default=str)
            
            cache.set(key, value, timeout)
            logger.debug(f"Cache set: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    @classmethod
    def get(cls, key: str, default: Any = None, prefix: str = None) -> Any:
        """Get cache value with optional prefix"""
        if prefix:
            key = cls.get_cache_key(prefix, key)
        
        try:
            value = cache.get(key, default)
            logger.debug(f"Cache get: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return default
    
    @classmethod
    def delete(cls, key: str, prefix: str = None) -> bool:
        """Delete cache value with optional prefix"""
        if prefix:
            key = cls.get_cache_key(prefix, key)
        
        try:
            cache.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            # This would work with Redis backend
            if hasattr(cache, 'delete_pattern'):
                return cache.delete_pattern(pattern)
            else:
                logger.warning("Pattern deletion not supported with current cache backend")
                return 0
        except Exception as e:
            logger.error(f"Cache pattern delete error: {e}")
            return 0
    
    @classmethod
    def get_or_set(cls, key: str, callable_func: Callable, timeout: Optional[int] = None, prefix: str = None) -> Any:
        """Get from cache or set using callable"""
        if prefix:
            key = cls.get_cache_key(prefix, key)
        
        try:
            return cache.get_or_set(key, callable_func, timeout)
        except Exception as e:
            logger.error(f"Cache get_or_set error: {e}")
            return callable_func()

def cache_result(timeout: int = 300, prefix: str = None, key_func: Callable = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Use function name and arguments hash
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            result = CacheManager.get(cache_key, prefix=prefix)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, timeout=timeout, prefix=prefix)
            logger.debug(f"Cache set for {func.__name__}")
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str, prefix: str = None):
    """Decorator to invalidate cache after function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache
            if prefix:
                pattern = CacheManager.get_cache_key(prefix, pattern)
            
            CacheManager.delete_pattern(pattern)
            logger.debug(f"Cache invalidated for pattern: {pattern}")
            
            return result
        return wrapper
    return decorator

class ProductCache:
    """Product-specific caching utilities"""
    
    @staticmethod
    @cache_result(timeout=1800, prefix='product')
    def get_featured_products():
        """Cache featured products"""
        from products.models import Product
        return list(Product.objects.filter(featured_product=True, is_active=True).select_related('category', 'seller'))
    
    @staticmethod
    @cache_result(timeout=1800, prefix='product')
    def get_best_sellers():
        """Cache best seller products"""
        from products.models import Product
        return list(Product.objects.filter(best_seller_product=True, is_active=True).select_related('category', 'seller'))
    
    @staticmethod
    @cache_result(timeout=1800, prefix='product')
    def get_flash_sale_products():
        """Cache flash sale products"""
        from products.models import Product
        return list(Product.objects.filter(flash_sale=True, is_active=True).select_related('category', 'seller'))
    
    @staticmethod
    def get_product_by_id(product_id: int):
        """Get product by ID with caching"""
        cache_key = f"product_detail_{product_id}"
        product = CacheManager.get(cache_key, prefix='product')
        
        if product is None:
            from products.models import Product
            try:
                product = Product.objects.select_related('category', 'seller').get(id=product_id)
                CacheManager.set(cache_key, product, timeout=1800, prefix='product')
            except Product.DoesNotExist:
                return None
        
        return product
    
    @staticmethod
    @invalidate_cache('product*')
    def invalidate_product_cache():
        """Invalidate all product-related cache"""
        pass

class CategoryCache:
    """Category-specific caching utilities"""
    
    @staticmethod
    @cache_result(timeout=7200, prefix='category')
    def get_all_categories():
        """Cache all categories"""
        from products.models import Category
        return list(Category.objects.filter(is_active=True).prefetch_related('products'))
    
    @staticmethod
    def get_category_by_id(category_id: int):
        """Get category by ID with caching"""
        cache_key = f"category_detail_{category_id}"
        category = CacheManager.get(cache_key, prefix='category')
        
        if category is None:
            from products.models import Category
            try:
                category = Category.objects.prefetch_related('products').get(id=category_id)
                CacheManager.set(cache_key, category, timeout=7200, prefix='category')
            except Category.DoesNotExist:
                return None
        
        return category

class UserCache:
    """User-specific caching utilities"""
    
    @staticmethod
    def get_user_profile(user_id: int):
        """Get user profile with caching"""
        cache_key = f"user_profile_{user_id}"
        user = CacheManager.get(cache_key, prefix='user')
        
        if user is None:
            from accounts.models import CustomUser
            try:
                user = CustomUser.objects.get(id=user_id)
                CacheManager.set(cache_key, user, timeout=3600, prefix='user')
            except CustomUser.DoesNotExist:
                return None
        
        return user
    
    @staticmethod
    @invalidate_cache('user*')
    def invalidate_user_cache():
        """Invalidate all user-related cache"""
        pass

class SearchCache:
    """Search-specific caching utilities"""
    
    @staticmethod
    def get_search_results(query: str, filters: dict = None):
        """Get search results with caching"""
        # Create cache key from query and filters
        cache_data = f"{query}:{str(sorted(filters.items()) if filters else {})}"
        cache_key = hashlib.md5(cache_data.encode()).hexdigest()
        
        results = CacheManager.get(cache_key, prefix='search')
        if results is None:
            # Perform search and cache results
            from products.models import Product
            queryset = Product.objects.filter(is_active=True)
            
            if query:
                queryset = queryset.filter(title__icontains=query)
            
            if filters:
                if filters.get('category'):
                    queryset = queryset.filter(category_id=filters['category'])
                if filters.get('min_price'):
                    queryset = queryset.filter(price__gte=filters['min_price'])
                if filters.get('max_price'):
                    queryset = queryset.filter(price__lte=filters['max_price'])
            
            results = list(queryset.select_related('category', 'seller'))
            CacheManager.set(cache_key, results, timeout=900, prefix='search')
        
        return results

class AnalyticsCache:
    """Analytics-specific caching utilities"""
    
    @staticmethod
    @cache_result(timeout=3600, prefix='analytics')
    def get_sales_summary():
        """Cache sales summary"""
        from orders.models import Order
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        return {
            'today_sales': Order.objects.filter(
                created_at__date=today,
                status='DELIVERED'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            
            'week_sales': Order.objects.filter(
                created_at__date__gte=week_ago,
                status='DELIVERED'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            
            'month_sales': Order.objects.filter(
                created_at__date__gte=month_ago,
                status='DELIVERED'
            ).aggregate(total=Sum('total_amount'))['total'] or 0,
            
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='PENDING').count(),
        }

# Cache warming functions
def warm_cache():
    """Warm up frequently accessed cache"""
    logger.info("Starting cache warming...")
    
    try:
        # Warm product caches
        ProductCache.get_featured_products()
        ProductCache.get_best_sellers()
        ProductCache.get_flash_sale_products()
        
        # Warm category cache
        CategoryCache.get_all_categories()
        
        # Warm analytics cache
        AnalyticsCache.get_sales_summary()
        
        logger.info("Cache warming completed successfully")
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")

def clear_all_cache():
    """Clear all cache"""
    logger.info("Clearing all cache...")
    
    try:
        cache.clear()
        logger.info("All cache cleared successfully")
    except Exception as e:
        logger.error(f"Cache clearing failed: {e}")
