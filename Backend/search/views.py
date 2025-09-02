from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, F, Case, When, IntegerField
from django.core.paginator import Paginator
from products.models import Product, Category
from products.serializers import ProductSerializer
import logging

logger = logging.getLogger(__name__)


class AdvancedSearchView(APIView):
    """
    Advanced search with multiple filters, sorting, and relevance scoring
    """
    
    def get(self, request):
        try:
            # Get search parameters
            query = request.query_params.get('q', '').strip()
            category = request.query_params.get('category')
            min_price = request.query_params.get('min_price')
            max_price = request.query_params.get('max_price')
            seller = request.query_params.get('seller')
            sort_by = request.query_params.get('sort_by', 'relevance')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            
            # Start with base queryset
            products = Product.objects.select_related('category', 'seller').filter(is_active=True)
            
            # Apply search query
            if query:
                # Create search conditions with relevance scoring
                search_conditions = Q()
                
                # Exact title match (highest relevance)
                exact_title_match = Q(title__iexact=query)
                
                # Title contains (high relevance)
                title_contains = Q(title__icontains=query)
                
                # Description contains (medium relevance)
                description_contains = Q(description__icontains=query)
                
                # Category name contains (low relevance)
                category_contains = Q(category__name__icontains=query)
                
                # Seller name contains (low relevance)
                seller_contains = Q(seller__name__icontains=query)
                
                # Combine all conditions
                search_conditions = (
                    exact_title_match | 
                    title_contains | 
                    description_contains | 
                    category_contains | 
                    seller_contains
                )
                
                products = products.filter(search_conditions)
                
                # Add relevance scoring
                products = products.annotate(
                    relevance_score=Case(
                        When(title__iexact=query, then=100),
                        When(title__icontains=query, then=80),
                        When(description__icontains=query, then=60),
                        When(category__name__icontains=query, then=40),
                        When(seller__name__icontains=query, then=20),
                        default=0,
                        output_field=IntegerField()
                    )
                )
            
            # Apply filters
            if category:
                products = products.filter(category__name__icontains=category)
            
            if min_price:
                try:
                    min_price = float(min_price)
                    products = products.filter(price__gte=min_price)
                except ValueError:
                    pass
            
            if max_price:
                try:
                    max_price = float(max_price)
                    products = products.filter(price__lte=max_price)
                except ValueError:
                    pass
            
            if seller:
                products = products.filter(seller__name__icontains=seller)
            
            # Apply sorting
            if sort_by == 'price_low':
                products = products.order_by('price')
            elif sort_by == 'price_high':
                products = products.order_by('-price')
            elif sort_by == 'newest':
                products = products.order_by('-created_at')
            elif sort_by == 'oldest':
                products = products.order_by('created_at')
            elif sort_by == 'rating':
                products = products.order_by('-average_rating')
            elif sort_by == 'popularity':
                products = products.order_by('-user_count')
            elif sort_by == 'discount':
                products = products.filter(discount_percentage__gt=0).order_by('-discount_percentage')
            else:  # relevance or default
                if query:
                    products = products.order_by('-relevance_score', '-created_at')
                else:
                    products = products.order_by('-created_at')
            
            # Pagination
            paginator = Paginator(products, page_size)
            page_obj = paginator.get_page(page)
            
            # Serialize results
            serializer = ProductSerializer(page_obj.object_list, many=True)
            
            # Prepare response
            response_data = {
                'results': serializer.data,
                'pagination': {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                    'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                },
                'filters_applied': {
                    'query': query,
                    'category': category,
                    'min_price': min_price,
                    'max_price': max_price,
                    'seller': seller,
                    'sort_by': sort_by,
                }
            }
            
            logger.info(f"Search performed: {query}, Results: {paginator.count}")
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return Response(
                {'error': 'Search failed'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchSuggestionsView(APIView):
    """
    Provide search suggestions based on popular searches and product titles
    """
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if len(query) < 2:
            return Response({'suggestions': []})
        
        try:
            # Get product title suggestions
            product_suggestions = Product.objects.filter(
                title__icontains=query,
                is_active=True
            ).values_list('title', flat=True)[:5]
            
            # Get category suggestions
            category_suggestions = Category.objects.filter(
                name__icontains=query
            ).values_list('name', flat=True)[:3]
            
            # Combine and deduplicate suggestions
            suggestions = list(set(list(product_suggestions) + list(category_suggestions)))
            
            return Response({
                'suggestions': suggestions[:8]  # Limit to 8 suggestions
            })
            
        except Exception as e:
            logger.error(f"Search suggestions error: {str(e)}")
            return Response({'suggestions': []})


class FilterOptionsView(APIView):
    """
    Get available filter options for search
    """
    
    def get(self, request):
        try:
            # Get all categories
            categories = Category.objects.all().values('id', 'name')
            
            # Get price range
            price_range = Product.objects.filter(is_active=True).aggregate(
                min_price=models.Min('price'),
                max_price=models.Max('price')
            )
            
            # Get sellers
            sellers = Product.objects.filter(is_active=True).select_related('seller').values(
                'seller__id', 'seller__name'
            ).distinct()
            
            return Response({
                'categories': list(categories),
                'price_range': price_range,
                'sellers': list(sellers),
                'sort_options': [
                    {'value': 'relevance', 'label': 'Most Relevant'},
                    {'value': 'price_low', 'label': 'Price: Low to High'},
                    {'value': 'price_high', 'label': 'Price: High to Low'},
                    {'value': 'newest', 'label': 'Newest First'},
                    {'value': 'oldest', 'label': 'Oldest First'},
                    {'value': 'rating', 'label': 'Highest Rated'},
                    {'value': 'popularity', 'label': 'Most Popular'},
                    {'value': 'discount', 'label': 'Best Discounts'},
                ]
            })
            
        except Exception as e:
            logger.error(f"Filter options error: {str(e)}")
            return Response(
                {'error': 'Failed to get filter options'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
