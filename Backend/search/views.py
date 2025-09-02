"""
Search Views

This module contains views for advanced search functionality,
including full-text search, filtering, suggestions, and analytics.
"""

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Count, Avg, Max, Min, Prefetch
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.core.cache import cache
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import connection
import time
import json
import logging

from .models import (
    SearchQuery, SearchSuggestion, SearchFilter, SearchAnalytics,
    ProductSearchIndex, SearchSession, SearchClick
)
from .serializers import (
    SearchRequestSerializer, SearchResultSerializer, SearchSuggestionSerializer,
    SearchFilterSerializer, SearchAnalyticsSerializer, SearchQuerySerializer,
    SearchSessionSerializer, SearchClickSerializer, SearchStatsSerializer,
    AdvancedSearchSerializer, SearchRecommendationSerializer, SearchPerformanceSerializer
)
from products.models import Product, Category, Seller
from products.serializers import ProductSerializer

logger = logging.getLogger(__name__)


class AdvancedSearchView(APIView):
    """Advanced search with full-text search and filtering"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Perform advanced search"""
        start_time = time.time()
        
        # Serialize and validate request
        serializer = SearchRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        search_data = serializer.validated_data
        
        # Get or create search session
        session = self._get_or_create_search_session(request)
        
        # Perform search
        search_results = self._perform_search(search_data, request.user, session)
        
        # Calculate search time
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Create search query record
        search_query = self._create_search_query(search_data, request.user, session, search_results)
        
        # Get available filters
        available_filters = self._get_available_filters(search_data)
        
        # Get search suggestions
        suggestions = self._get_search_suggestions(search_data.get('query', ''))
        
        # Prepare response data
        response_data = {
            'query': search_data.get('query', ''),
            'total_results': search_results['total_count'],
            'page': search_data.get('page', 1),
            'page_size': search_data.get('page_size', 20),
            'total_pages': search_results['total_pages'],
            'products': search_results['products'],
            'applied_filters': self._get_applied_filters(search_data),
            'available_filters': available_filters,
            'suggestions': suggestions,
            'search_time': search_time,
            'cache_hit': search_results.get('cache_hit', False)
        }
        
        # Cache results for performance
        self._cache_search_results(search_data, response_data)
        
        # Log search analytics
        self._log_search_analytics(search_query, search_time)
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _get_or_create_search_session(self, request):
        """Get or create search session"""
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        session, created = SearchSession.objects.get_or_create(
            session_id=session_id,
            defaults={'user': request.user if request.user.is_authenticated else None}
        )
        
        if not created:
            session.last_activity = timezone.now()
            session.save()
        
        return session
    
    def _perform_search(self, search_data, user, session):
        """Perform the actual search"""
        query = search_data.get('query', '')
        page = search_data.get('page', 1)
        page_size = search_data.get('page_size', 20)
        sort_by = search_data.get('sort_by', 'relevance')
        
        # Check cache first
        cache_key = self._get_cache_key(search_data)
        cached_results = cache.get(cache_key)
        if cached_results:
            cached_results['cache_hit'] = True
            return cached_results
        
        # Build search query
        search_queryset = self._build_search_queryset(search_data)
        
        # Apply sorting
        search_queryset = self._apply_sorting(search_queryset, sort_by, query)
        
        # Get total count
        total_count = search_queryset.count()
        
        # Apply pagination
        paginator = Paginator(search_queryset, page_size)
        total_pages = paginator.num_pages
        
        try:
            page_obj = paginator.page(page)
            products = page_obj.object_list
        except:
            products = []
        
        # Serialize products
        product_serializer = ProductSerializer(products, many=True, context={'request': None})
        
        return {
            'products': product_serializer.data,
            'total_count': total_count,
            'total_pages': total_pages,
            'cache_hit': False
        }
    
    def _build_search_queryset(self, search_data):
        """Build the search queryset with filters"""
        queryset = Product.objects.select_related('category', 'seller').prefetch_related('images')
        
        # Text search
        query = search_data.get('query', '')
        if query:
            # Use full-text search if available, otherwise use basic search
            if hasattr(Product, 'search_vector'):
                search_vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
                search_query = SearchQuery(query)
                queryset = queryset.annotate(
                    search_rank=SearchRank(search_vector, search_query)
                ).filter(search_vector=search_query)
            else:
                # Fallback to basic search
                queryset = queryset.filter(
                    Q(title__icontains=query) | 
                    Q(description__icontains=query) |
                    Q(category__name__icontains=query) |
                    Q(seller__name__icontains=query)
                )
        
        # Category filter
        category = search_data.get('category')
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        
        # Price range filter
        price_min = search_data.get('price_min')
        price_max = search_data.get('price_max')
        if price_min is not None:
            queryset = queryset.filter(price__gte=price_min)
        if price_max is not None:
            queryset = queryset.filter(price__lte=price_max)
        
        # Seller filter
        seller = search_data.get('seller')
        if seller:
            queryset = queryset.filter(seller__name__icontains=seller)
        
        # Rating filter
        rating_min = search_data.get('rating_min')
        if rating_min is not None:
            queryset = queryset.filter(rating__gte=rating_min)
        
        # Boolean filters
        if search_data.get('featured') is True:
            queryset = queryset.filter(featured_product=True)
        
        if search_data.get('best_seller') is True:
            queryset = queryset.filter(best_seller_product=True)
        
        if search_data.get('flash_sale') is True:
            queryset = queryset.filter(flash_sale=True)
        
        if search_data.get('in_stock') is True:
            queryset = queryset.filter(stock__gt=0)
        
        return queryset
    
    def _apply_sorting(self, queryset, sort_by, query):
        """Apply sorting to the queryset"""
        if sort_by == 'relevance' and query:
            # Sort by search rank if available
            if hasattr(Product, 'search_vector'):
                return queryset.order_by('-search_rank', '-created_at')
            else:
                return queryset.order_by('-created_at')
        elif sort_by == 'price_low':
            return queryset.order_by('price')
        elif sort_by == 'price_high':
            return queryset.order_by('-price')
        elif sort_by == 'rating':
            return queryset.order_by('-rating', '-created_at')
        elif sort_by == 'newest':
            return queryset.order_by('-created_at')
        elif sort_by == 'popularity':
            return queryset.order_by('-views', '-created_at')
        else:
            return queryset.order_by('-created_at')
    
    def _get_available_filters(self, search_data):
        """Get available filters for the current search"""
        # Get all active filters
        filters = SearchFilter.objects.filter(is_active=True).order_by('display_order')
        
        # Get filter values based on current search results
        base_queryset = self._build_search_queryset(search_data)
        
        available_filters = []
        for filter_obj in filters:
            filter_data = {
                'id': filter_obj.id,
                'filter_type': filter_obj.filter_type,
                'filter_name': filter_obj.filter_name,
                'filter_key': filter_obj.filter_key,
                'is_required': filter_obj.is_required,
                'display_order': filter_obj.display_order,
                'options': []
            }
            
            # Get filter options based on type
            if filter_obj.filter_type == 'CATEGORY':
                categories = base_queryset.values('category__name').distinct()
                filter_data['options'] = [{'value': cat['category__name'], 'count': 0} for cat in categories]
            elif filter_obj.filter_type == 'SELLER':
                sellers = base_queryset.values('seller__name').distinct()
                filter_data['options'] = [{'value': seller['seller__name'], 'count': 0} for seller in sellers]
            elif filter_obj.filter_type == 'PRICE_RANGE':
                price_stats = base_queryset.aggregate(
                    min_price=Min('price'),
                    max_price=Max('price')
                )
                filter_data['options'] = [price_stats]
            
            available_filters.append(filter_data)
        
        return available_filters
    
    def _get_search_suggestions(self, query):
        """Get search suggestions based on query"""
        if not query or len(query) < 2:
            return []
        
        # Get suggestions that match the query
        suggestions = SearchSuggestion.objects.filter(
            suggestion__icontains=query,
            is_active=True
        ).order_by('-priority', '-search_count')[:10]
        
        return SearchSuggestionSerializer(suggestions, many=True).data
    
    def _get_applied_filters(self, search_data):
        """Get currently applied filters"""
        applied_filters = {}
        
        for key, value in search_data.items():
            if key not in ['query', 'page', 'page_size', 'sort_by'] and value is not None:
                applied_filters[key] = value
        
        return applied_filters
    
    def _create_search_query(self, search_data, user, session, search_results):
        """Create search query record for analytics"""
        search_query = SearchQuery.objects.create(
            query=search_data.get('query', ''),
            user=user if user.is_authenticated else None,
            session_id=session.session_id,
            results_count=search_results['total_count'],
            has_results=search_results['total_count'] > 0
        )
        
        # Update session
        session.search_queries.append(search_data.get('query', ''))
        session.total_searches += 1
        session.save()
        
        return search_query
    
    def _get_cache_key(self, search_data):
        """Generate cache key for search results"""
        cache_data = {k: v for k, v in search_data.items() if k not in ['page']}
        return f"search:{hash(str(sorted(cache_data.items())))}"
    
    def _cache_search_results(self, search_data, response_data):
        """Cache search results"""
        cache_key = self._get_cache_key(search_data)
        cache.set(cache_key, response_data, timeout=300)  # 5 minutes
    
    def _log_search_analytics(self, search_query, search_time):
        """Log search analytics"""
        # Update daily analytics
        today = timezone.now().date()
        analytics, created = SearchAnalytics.objects.get_or_create(
            date=today,
            defaults={
                'total_searches': 0,
                'unique_searches': 0,
                'searches_with_results': 0,
                'searches_without_results': 0,
                'average_search_time': 0.0
            }
        )
        
        analytics.total_searches += 1
        if search_query.has_results:
            analytics.searches_with_results += 1
        else:
            analytics.searches_without_results += 1
        
        # Update average search time
        total_time = analytics.average_search_time * (analytics.total_searches - 1) + search_time
        analytics.average_search_time = total_time / analytics.total_searches
        analytics.save()


class SearchSuggestionsView(APIView):
    """Get search suggestions and autocomplete"""
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Get search suggestions"""
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))
        
        if len(query) < 2:
            return Response({'suggestions': []})
        
        # Get suggestions from database
        suggestions = SearchSuggestion.objects.filter(
            suggestion__icontains=query,
            is_active=True
        ).order_by('-priority', '-search_count')[:limit]
        
        # Get popular searches
        popular_searches = SearchQuery.objects.filter(
            query__icontains=query,
            has_results=True
        ).values('query').annotate(
            count=Count('query')
        ).order_by('-count')[:limit]
        
        # Combine suggestions
        all_suggestions = []
        
        # Add database suggestions
        for suggestion in suggestions:
            all_suggestions.append({
                'text': suggestion.suggestion,
                'type': suggestion.suggestion_type,
                'category': suggestion.category.name if suggestion.category else None,
                'product': suggestion.product.title if suggestion.product else None,
                'seller': suggestion.seller.name if suggestion.seller else None
            })
        
        # Add popular searches
        for search in popular_searches:
            if search['query'] not in [s['text'] for s in all_suggestions]:
                all_suggestions.append({
                    'text': search['query'],
                    'type': 'POPULAR',
                    'count': search['count']
                })
        
        return Response({'suggestions': all_suggestions[:limit]})


class SearchAnalyticsView(APIView):
    """Search analytics and statistics"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get search analytics"""
        # Get date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Get analytics data
        analytics_queryset = SearchAnalytics.objects.all()
        
        if start_date:
            analytics_queryset = analytics_queryset.filter(date__gte=start_date)
        if end_date:
            analytics_queryset = analytics_queryset.filter(date__lte=end_date)
        
        analytics = analytics_queryset.order_by('-date')[:30]  # Last 30 days
        
        # Get search statistics
        total_searches = analytics_queryset.aggregate(
            total=Count('total_searches')
        )['total'] or 0
        
        unique_queries = SearchQuery.objects.filter(
            created_at__gte=start_date if start_date else timezone.now() - timezone.timedelta(days=30)
        ).values('query').distinct().count()
        
        # Get top searches
        top_searches = SearchQuery.objects.filter(
            created_at__gte=start_date if start_date else timezone.now() - timezone.timedelta(days=30)
        ).values('query').annotate(
            count=Count('query')
        ).order_by('-count')[:10]
        
        # Get search trends
        search_trends = {}
        for analytic in analytics:
            search_trends[str(analytic.date)] = {
                'total_searches': analytic.total_searches,
                'unique_searches': analytic.unique_searches,
                'searches_with_results': analytic.searches_with_results,
                'average_search_time': analytic.average_search_time
            }
        
        # Get filter usage
        filter_usage = {}
        filters = SearchFilter.objects.filter(is_active=True)
        for filter_obj in filters:
            filter_usage[filter_obj.filter_name] = filter_obj.usage_count
        
        # Get conversion rates
        conversion_rates = {}
        total_clicks = analytics_queryset.aggregate(total=Count('total_clicks'))['total'] or 0
        total_conversions = analytics_queryset.aggregate(total=Count('total_conversions'))['total'] or 0
        
        if total_clicks > 0:
            conversion_rates['overall'] = (total_conversions / total_clicks) * 100
        
        response_data = {
            'total_searches': total_searches,
            'unique_queries': unique_queries,
            'average_results_per_search': 0,  # Calculate from analytics
            'top_searches': [search['query'] for search in top_searches],
            'search_trends': search_trends,
            'filter_usage': filter_usage,
            'conversion_rates': conversion_rates,
            'analytics': SearchAnalyticsSerializer(analytics, many=True).data
        }
        
        return Response(response_data)


class SearchClickView(APIView):
    """Track search result clicks"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Record a search result click"""
        serializer = SearchClickSerializer(data=request.data)
        if serializer.is_valid():
            click = serializer.save()
            
            # Update search query click count
            if click.search_query:
                click.search_query.clicked_results += 1
                click.search_query.save()
            
            # Update search session
            if click.session:
                click.session.clicked_products.append(click.product.id)
                click.session.total_clicks += 1
                click.session.save()
            
            # Update search suggestion click count
            suggestion = SearchSuggestion.objects.filter(
                suggestion=click.search_query.query
            ).first()
            if suggestion:
                suggestion.click_count += 1
                suggestion.save()
            
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchPerformanceView(APIView):
    """Search performance monitoring"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get search performance metrics"""
        # Get performance data from cache or database
        performance_data = cache.get('search_performance', {})
        
        # Get database query performance
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public' 
                AND tablename IN ('products_product', 'search_searchquery')
            """)
            db_stats = cursor.fetchall()
        
        # Get cache performance
        cache_stats = cache.get('cache_stats', {
            'hit_rate': 0.0,
            'miss_rate': 0.0,
            'total_requests': 0
        })
        
        response_data = {
            'database_stats': db_stats,
            'cache_stats': cache_stats,
            'performance_metrics': performance_data,
            'recommendations': self._get_performance_recommendations(performance_data)
        }
        
        return Response(response_data)
    
    def _get_performance_recommendations(self, performance_data):
        """Get performance improvement recommendations"""
        recommendations = []
        
        if performance_data.get('average_search_time', 0) > 500:  # 500ms
            recommendations.append("Consider adding more database indexes for search queries")
        
        if performance_data.get('cache_hit_rate', 0) < 0.8:  # 80%
            recommendations.append("Increase cache timeout or improve cache key strategy")
        
        if performance_data.get('database_queries', 0) > 10:
            recommendations.append("Optimize database queries to reduce N+1 problems")
        
        return recommendations