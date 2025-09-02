"""
Advanced Analytics and Reporting System
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, F, Case, When, IntegerField
from django.core.cache import cache
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

User = get_user_model()
logger = logging.getLogger(__name__)

class AnalyticsEvent(models.Model):
    """Track analytics events"""
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('product_view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('remove_from_cart', 'Remove from Cart'),
        ('purchase', 'Purchase'),
        ('search', 'Search'),
        ('category_view', 'Category View'),
        ('user_registration', 'User Registration'),
        ('user_login', 'User Login'),
        ('email_click', 'Email Click'),
        ('social_share', 'Social Share'),
        ('review_submitted', 'Review Submitted'),
        ('wishlist_add', 'Wishlist Add'),
        ('wishlist_remove', 'Wishlist Remove'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    session_id = models.CharField(max_length=100, blank=True)
    
    # Event data
    event_data = models.JSONField(default=dict, help_text="Event-specific data")
    metadata = models.JSONField(default=dict, help_text="Additional event metadata")
    
    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Related objects
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    category = models.ForeignKey('products.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics_events')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['event_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_id', 'created_at']),
            models.Index(fields=['product', 'created_at']),
            models.Index(fields=['category', 'created_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user or 'Anonymous'} - {self.created_at}"

class ProductAnalytics(models.Model):
    """Product-specific analytics"""
    product = models.OneToOneField('products.Product', on_delete=models.CASCADE, related_name='analytics')
    
    # View metrics
    total_views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    views_today = models.PositiveIntegerField(default=0)
    views_this_week = models.PositiveIntegerField(default=0)
    views_this_month = models.PositiveIntegerField(default=0)
    
    # Conversion metrics
    add_to_cart_count = models.PositiveIntegerField(default=0)
    purchase_count = models.PositiveIntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0, help_text="Purchase/View ratio")
    
    # Revenue metrics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue_today = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue_this_week = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue_this_month = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Rating metrics
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Search metrics
    search_appearances = models.PositiveIntegerField(default=0)
    search_clicks = models.PositiveIntegerField(default=0)
    search_click_through_rate = models.FloatField(default=0.0)
    
    # Timestamps
    last_viewed = models.DateTimeField(null=True, blank=True)
    last_purchased = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['conversion_rate']),
            models.Index(fields=['total_revenue']),
            models.Index(fields=['average_rating']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.product.title}"
    
    def update_metrics(self):
        """Update all analytics metrics"""
        try:
            # Update view metrics
            self.total_views = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='product_view'
            ).count()
            
            self.unique_views = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='product_view'
            ).values('user').distinct().count()
            
            # Update time-based metrics
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            self.views_today = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='product_view',
                created_at__date=today
            ).count()
            
            self.views_this_week = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='product_view',
                created_at__date__gte=week_ago
            ).count()
            
            self.views_this_month = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='product_view',
                created_at__date__gte=month_ago
            ).count()
            
            # Update conversion metrics
            self.add_to_cart_count = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='add_to_cart'
            ).count()
            
            self.purchase_count = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='purchase'
            ).count()
            
            # Calculate conversion rate
            if self.total_views > 0:
                self.conversion_rate = (self.purchase_count / self.total_views) * 100
            
            # Update revenue metrics
            from orders.models import OrderItem
            order_items = OrderItem.objects.filter(product=self.product)
            
            self.total_revenue = order_items.aggregate(
                total=Sum(F('quantity') * F('price'))
            )['total'] or 0
            
            # Update time-based revenue
            self.revenue_today = order_items.filter(
                order__created_at__date=today
            ).aggregate(
                total=Sum(F('quantity') * F('price'))
            )['total'] or 0
            
            self.revenue_this_week = order_items.filter(
                order__created_at__date__gte=week_ago
            ).aggregate(
                total=Sum(F('quantity') * F('price'))
            )['total'] or 0
            
            self.revenue_this_month = order_items.filter(
                order__created_at__date__gte=month_ago
            ).aggregate(
                total=Sum(F('quantity') * F('price'))
            )['total'] or 0
            
            # Update rating metrics
            from products.models import Review
            reviews = Review.objects.filter(product=self.product)
            
            self.total_reviews = reviews.count()
            if self.total_reviews > 0:
                self.average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
            
            # Update search metrics
            search_events = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='search'
            )
            
            self.search_appearances = search_events.count()
            self.search_clicks = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='product_view',
                event_data__search_query__isnull=False
            ).count()
            
            if self.search_appearances > 0:
                self.search_click_through_rate = (self.search_clicks / self.search_appearances) * 100
            
            # Update timestamps
            last_view = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='product_view'
            ).order_by('-created_at').first()
            
            if last_view:
                self.last_viewed = last_view.created_at
            
            last_purchase = AnalyticsEvent.objects.filter(
                product=self.product,
                event_type='purchase'
            ).order_by('-created_at').first()
            
            if last_purchase:
                self.last_purchased = last_purchase.created_at
            
            self.save()
            
        except Exception as e:
            logger.error(f"Error updating product analytics: {e}")

class SalesAnalytics(models.Model):
    """Sales analytics and reporting"""
    date = models.DateField(unique=True)
    
    # Sales metrics
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Customer metrics
    new_customers = models.PositiveIntegerField(default=0)
    returning_customers = models.PositiveIntegerField(default=0)
    total_customers = models.PositiveIntegerField(default=0)
    
    # Product metrics
    products_sold = models.PositiveIntegerField(default=0)
    unique_products_sold = models.PositiveIntegerField(default=0)
    
    # Conversion metrics
    cart_abandonment_rate = models.FloatField(default=0.0)
    checkout_conversion_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['total_revenue']),
            models.Index(fields=['total_orders']),
        ]
        ordering = ['-date']
    
    def __str__(self):
        return f"Sales Analytics - {self.date}"
    
    @classmethod
    def update_daily_analytics(cls, date=None):
        """Update daily sales analytics"""
        if date is None:
            date = timezone.now().date()
        
        try:
            # Get or create analytics record
            analytics, created = cls.objects.get_or_create(date=date)
            
            # Calculate sales metrics
            from orders.models import Order, OrderItem
            
            orders = Order.objects.filter(created_at__date=date)
            analytics.total_orders = orders.count()
            
            if analytics.total_orders > 0:
                analytics.total_revenue = orders.aggregate(
                    total=Sum('total_amount')
                )['total'] or 0
                
                analytics.average_order_value = analytics.total_revenue / analytics.total_orders
            
            # Calculate customer metrics
            customer_orders = orders.values('user').distinct()
            analytics.total_customers = customer_orders.count()
            
            # New vs returning customers
            first_time_customers = 0
            for customer_order in customer_orders:
                user_id = customer_order['user']
                if user_id:
                    previous_orders = Order.objects.filter(
                        user_id=user_id,
                        created_at__date__lt=date
                    ).count()
                    if previous_orders == 0:
                        first_time_customers += 1
            
            analytics.new_customers = first_time_customers
            analytics.returning_customers = analytics.total_customers - first_time_customers
            
            # Calculate product metrics
            order_items = OrderItem.objects.filter(order__created_at__date=date)
            analytics.products_sold = order_items.aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            analytics.unique_products_sold = order_items.values('product').distinct().count()
            
            # Calculate conversion metrics
            cart_events = AnalyticsEvent.objects.filter(
                event_type='add_to_cart',
                created_at__date=date
            ).count()
            
            purchase_events = AnalyticsEvent.objects.filter(
                event_type='purchase',
                created_at__date=date
            ).count()
            
            if cart_events > 0:
                analytics.cart_abandonment_rate = ((cart_events - purchase_events) / cart_events) * 100
                analytics.checkout_conversion_rate = (purchase_events / cart_events) * 100
            
            analytics.save()
            
        except Exception as e:
            logger.error(f"Error updating daily analytics: {e}")

class AnalyticsDashboard:
    """Analytics dashboard data provider"""
    
    @staticmethod
    def get_overview_metrics(period: str = '30d') -> Dict[str, Any]:
        """Get overview metrics for dashboard"""
        try:
            # Calculate date range
            end_date = timezone.now().date()
            if period == '7d':
                start_date = end_date - timedelta(days=7)
            elif period == '30d':
                start_date = end_date - timedelta(days=30)
            elif period == '90d':
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get sales analytics
            sales_data = SalesAnalytics.objects.filter(
                date__range=[start_date, end_date]
            ).aggregate(
                total_orders=Sum('total_orders'),
                total_revenue=Sum('total_revenue'),
                total_customers=Sum('total_customers'),
                avg_order_value=Avg('average_order_value')
            )
            
            # Get user metrics
            user_metrics = User.objects.filter(
                date_joined__date__range=[start_date, end_date]
            ).aggregate(
                new_users=Count('id'),
                active_users=Count('id', filter=Q(last_login__date__range=[start_date, end_date]))
            )
            
            # Get product metrics
            from products.models import Product
            product_metrics = Product.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).aggregate(
                new_products=Count('id'),
                active_products=Count('id', filter=Q(is_active=True))
            )
            
            # Get event metrics
            event_metrics = AnalyticsEvent.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).aggregate(
                total_events=Count('id'),
                unique_sessions=Count('session_id', distinct=True)
            )
            
            return {
                'period': period,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'sales': {
                    'total_orders': sales_data['total_orders'] or 0,
                    'total_revenue': float(sales_data['total_revenue'] or 0),
                    'total_customers': sales_data['total_customers'] or 0,
                    'average_order_value': float(sales_data['avg_order_value'] or 0)
                },
                'users': {
                    'new_users': user_metrics['new_users'] or 0,
                    'active_users': user_metrics['active_users'] or 0
                },
                'products': {
                    'new_products': product_metrics['new_products'] or 0,
                    'active_products': product_metrics['active_products'] or 0
                },
                'engagement': {
                    'total_events': event_metrics['total_events'] or 0,
                    'unique_sessions': event_metrics['unique_sessions'] or 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting overview metrics: {e}")
            return {}
    
    @staticmethod
    def get_sales_trends(period: str = '30d') -> List[Dict[str, Any]]:
        """Get sales trends data"""
        try:
            # Calculate date range
            end_date = timezone.now().date()
            if period == '7d':
                start_date = end_date - timedelta(days=7)
            elif period == '30d':
                start_date = end_date - timedelta(days=30)
            elif period == '90d':
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get daily sales data
            sales_data = SalesAnalytics.objects.filter(
                date__range=[start_date, end_date]
            ).order_by('date')
            
            trends = []
            for data in sales_data:
                trends.append({
                    'date': data.date.isoformat(),
                    'orders': data.total_orders,
                    'revenue': float(data.total_revenue),
                    'customers': data.total_customers,
                    'avg_order_value': float(data.average_order_value)
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting sales trends: {e}")
            return []
    
    @staticmethod
    def get_top_products(limit: int = 10, period: str = '30d') -> List[Dict[str, Any]]:
        """Get top performing products"""
        try:
            # Calculate date range
            end_date = timezone.now().date()
            if period == '7d':
                start_date = end_date - timedelta(days=7)
            elif period == '30d':
                start_date = end_date - timedelta(days=30)
            elif period == '90d':
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get product analytics
            from products.models import Product
            products = Product.objects.filter(
                analytics__isnull=False,
                created_at__date__lte=end_date
            ).select_related('analytics', 'category', 'seller').order_by(
                '-analytics__total_revenue'
            )[:limit]
            
            top_products = []
            for product in products:
                analytics = product.analytics
                top_products.append({
                    'id': product.id,
                    'title': product.title,
                    'category': product.category.name if product.category else None,
                    'seller': product.seller.name if product.seller else None,
                    'price': float(product.price),
                    'total_views': analytics.total_views,
                    'total_revenue': float(analytics.total_revenue),
                    'conversion_rate': analytics.conversion_rate,
                    'average_rating': analytics.average_rating,
                    'total_reviews': analytics.total_reviews
                })
            
            return top_products
            
        except Exception as e:
            logger.error(f"Error getting top products: {e}")
            return []
    
    @staticmethod
    def get_category_performance(period: str = '30d') -> List[Dict[str, Any]]:
        """Get category performance metrics"""
        try:
            # Calculate date range
            end_date = timezone.now().date()
            if period == '7d':
                start_date = end_date - timedelta(days=7)
            elif period == '30d':
                start_date = end_date - timedelta(days=30)
            elif period == '90d':
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get category analytics
            from products.models import Category
            from orders.models import OrderItem
            
            categories = Category.objects.annotate(
                total_products=Count('products'),
                active_products=Count('products', filter=Q(products__is_active=True)),
                total_revenue=Sum(
                    'products__orderitem__quantity' * 'products__orderitem__price',
                    filter=Q(products__orderitem__order__created_at__date__range=[start_date, end_date])
                ),
                total_orders=Count(
                    'products__orderitem__order',
                    filter=Q(products__orderitem__order__created_at__date__range=[start_date, end_date]),
                    distinct=True
                )
            ).order_by('-total_revenue')
            
            category_performance = []
            for category in categories:
                category_performance.append({
                    'id': category.id,
                    'name': category.name,
                    'total_products': category.total_products,
                    'active_products': category.active_products,
                    'total_revenue': float(category.total_revenue or 0),
                    'total_orders': category.total_orders
                })
            
            return category_performance
            
        except Exception as e:
            logger.error(f"Error getting category performance: {e}")
            return []
    
    @staticmethod
    def get_user_behavior_insights(period: str = '30d') -> Dict[str, Any]:
        """Get user behavior insights"""
        try:
            # Calculate date range
            end_date = timezone.now().date()
            if period == '7d':
                start_date = end_date - timedelta(days=7)
            elif period == '30d':
                start_date = end_date - timedelta(days=30)
            elif period == '90d':
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get event analytics
            events = AnalyticsEvent.objects.filter(
                created_at__date__range=[start_date, end_date]
            )
            
            # Event type distribution
            event_distribution = events.values('event_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # User engagement metrics
            user_engagement = events.values('user').annotate(
                event_count=Count('id')
            ).aggregate(
                avg_events_per_user=Avg('event_count'),
                max_events_per_user=Count('event_count')
            )
            
            # Session analytics
            session_metrics = events.values('session_id').annotate(
                event_count=Count('id')
            ).aggregate(
                avg_events_per_session=Avg('event_count'),
                total_sessions=Count('session_id', distinct=True)
            )
            
            return {
                'event_distribution': list(event_distribution),
                'user_engagement': {
                    'avg_events_per_user': user_engagement['avg_events_per_user'] or 0,
                    'max_events_per_user': user_engagement['max_events_per_user'] or 0
                },
                'session_metrics': {
                    'avg_events_per_session': session_metrics['avg_events_per_session'] or 0,
                    'total_sessions': session_metrics['total_sessions'] or 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user behavior insights: {e}")
            return {}

class AnalyticsTracker:
    """Track analytics events"""
    
    @staticmethod
    def track_event(event_type: str, user: User = None, product=None, category=None,
                   order=None, event_data: Dict = None, metadata: Dict = None,
                   session_id: str = None, request=None):
        """Track an analytics event"""
        try:
            event = AnalyticsEvent.objects.create(
                event_type=event_type,
                user=user,
                product=product,
                category=category,
                order=order,
                event_data=event_data or {},
                metadata=metadata or {},
                session_id=session_id or '',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
                referrer=request.META.get('HTTP_REFERER', '') if request else ''
            )
            
            # Update product analytics if applicable
            if product and event_type in ['product_view', 'add_to_cart', 'purchase']:
                try:
                    product_analytics, created = ProductAnalytics.objects.get_or_create(
                        product=product
                    )
                    product_analytics.update_metrics()
                except Exception as e:
                    logger.error(f"Error updating product analytics: {e}")
            
            logger.info(f"Tracked event: {event_type} - {user or 'Anonymous'}")
            return event
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            return None
    
    @staticmethod
    def get_user_analytics(user: User, period: str = '30d') -> Dict[str, Any]:
        """Get analytics for a specific user"""
        try:
            # Calculate date range
            end_date = timezone.now().date()
            if period == '7d':
                start_date = end_date - timedelta(days=7)
            elif period == '30d':
                start_date = end_date - timedelta(days=30)
            elif period == '90d':
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get user events
            events = AnalyticsEvent.objects.filter(
                user=user,
                created_at__date__range=[start_date, end_date]
            )
            
            # Event summary
            event_summary = events.values('event_type').annotate(
                count=Count('id')
            ).order_by('-count')
            
            # Product interactions
            product_interactions = events.filter(
                product__isnull=False
            ).values('product__title', 'product__id').annotate(
                interactions=Count('id')
            ).order_by('-interactions')[:10]
            
            # Category preferences
            category_preferences = events.filter(
                category__isnull=False
            ).values('category__name', 'category__id').annotate(
                interactions=Count('id')
            ).order_by('-interactions')[:5]
            
            return {
                'period': period,
                'total_events': events.count(),
                'event_summary': list(event_summary),
                'product_interactions': list(product_interactions),
                'category_preferences': list(category_preferences),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {e}")
            return {}

# Global analytics tracker instance
analytics_tracker = AnalyticsTracker()
