"""
Advanced Product Recommendation Engine
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache
from typing import List, Dict, Any, Optional
import json
import logging
from collections import defaultdict, Counter
import math

User = get_user_model()
logger = logging.getLogger(__name__)

class ProductRecommendation(models.Model):
    """Store product recommendations for users"""
    RECOMMENDATION_TYPES = [
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based'),
        ('hybrid', 'Hybrid'),
        ('trending', 'Trending'),
        ('similar', 'Similar Products'),
        ('frequently_bought', 'Frequently Bought Together'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    score = models.FloatField(help_text="Recommendation confidence score (0-1)")
    algorithm = models.CharField(max_length=50, help_text="Algorithm used for recommendation")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional recommendation data")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="When this recommendation expires")
    
    class Meta:
        unique_together = ['user', 'product', 'recommendation_type']
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['product', 'recommendation_type']),
            models.Index(fields=['score', 'created_at']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"{self.user.phone} - {self.product.title} ({self.get_recommendation_type_display()})"
    
    def is_expired(self):
        """Check if recommendation has expired"""
        return timezone.now() > self.expires_at

class UserBehavior(models.Model):
    """Track user behavior for recommendations"""
    BEHAVIOR_TYPES = [
        ('view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('remove_from_cart', 'Remove from Cart'),
        ('purchase', 'Purchase'),
        ('wishlist', 'Add to Wishlist'),
        ('review', 'Product Review'),
        ('search', 'Search Query'),
        ('category_view', 'Category View'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='behaviors')
    behavior_type = models.CharField(max_length=20, choices=BEHAVIOR_TYPES)
    
    # Related objects
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True, related_name='behaviors')
    category = models.ForeignKey('products.Category', on_delete=models.CASCADE, null=True, blank=True, related_name='behaviors')
    
    # Behavior data
    value = models.FloatField(default=1.0, help_text="Behavior weight/importance")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional behavior data")
    
    # Context
    session_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'behavior_type', 'created_at']),
            models.Index(fields=['product', 'behavior_type']),
            models.Index(fields=['category', 'behavior_type']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.phone} - {self.get_behavior_type_display()} - {self.product or self.category}"

class RecommendationEngine:
    """Main recommendation engine class"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        self.min_interactions = 5  # Minimum interactions for collaborative filtering
        self.recommendation_limit = 20
    
    def get_recommendations(self, user: User, limit: int = 10, 
                          recommendation_types: List[str] = None) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user"""
        if recommendation_types is None:
            recommendation_types = ['collaborative', 'content_based', 'trending']
        
        cache_key = f"recommendations:{user.id}:{':'.join(recommendation_types)}"
        cached_recommendations = cache.get(cache_key)
        
        if cached_recommendations:
            logger.info(f"Returning cached recommendations for user {user.id}")
            return cached_recommendations[:limit]
        
        recommendations = []
        
        # Get recommendations from different algorithms
        for rec_type in recommendation_types:
            if rec_type == 'collaborative':
                recs = self._collaborative_filtering(user)
            elif rec_type == 'content_based':
                recs = self._content_based_filtering(user)
            elif rec_type == 'trending':
                recs = self._trending_products()
            elif rec_type == 'similar':
                recs = self._similar_products(user)
            elif rec_type == 'frequently_bought':
                recs = self._frequently_bought_together(user)
            else:
                continue
            
            recommendations.extend(recs)
        
        # Remove duplicates and sort by score
        unique_recommendations = self._deduplicate_recommendations(recommendations)
        sorted_recommendations = sorted(unique_recommendations, key=lambda x: x['score'], reverse=True)
        
        # Cache results
        cache.set(cache_key, sorted_recommendations, self.cache_timeout)
        
        # Store recommendations in database
        self._store_recommendations(user, sorted_recommendations[:self.recommendation_limit])
        
        return sorted_recommendations[:limit]
    
    def _collaborative_filtering(self, user: User) -> List[Dict[str, Any]]:
        """Collaborative filtering based on user behavior similarity"""
        try:
            # Get users with similar behavior patterns
            similar_users = self._find_similar_users(user)
            
            if not similar_users:
                return []
            
            # Get products liked by similar users
            recommendations = []
            user_product_ids = set(
                UserBehavior.objects.filter(user=user, behavior_type='purchase')
                .values_list('product_id', flat=True)
            )
            
            for similar_user, similarity_score in similar_users:
                similar_user_products = UserBehavior.objects.filter(
                    user=similar_user,
                    behavior_type='purchase',
                    product__isnull=False
                ).exclude(product_id__in=user_product_ids)
                
                for behavior in similar_user_products:
                    recommendations.append({
                        'product': behavior.product,
                        'score': similarity_score * behavior.value,
                        'type': 'collaborative',
                        'algorithm': 'user_based_cf',
                        'metadata': {
                            'similar_user': similar_user.id,
                            'similarity_score': similarity_score
                        }
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {e}")
            return []
    
    def _content_based_filtering(self, user: User) -> List[Dict[str, Any]]:
        """Content-based filtering based on user preferences"""
        try:
            # Get user's preferred categories and product attributes
            user_preferences = self._get_user_preferences(user)
            
            if not user_preferences:
                return []
            
            # Find products similar to user's preferences
            from products.models import Product
            
            recommendations = []
            user_product_ids = set(
                UserBehavior.objects.filter(user=user, behavior_type='purchase')
                .values_list('product_id', flat=True)
            )
            
            # Get products from preferred categories
            for category_id, preference_score in user_preferences.get('categories', {}).items():
                products = Product.objects.filter(
                    category_id=category_id,
                    is_active=True
                ).exclude(id__in=user_product_ids)
                
                for product in products[:5]:  # Limit per category
                    recommendations.append({
                        'product': product,
                        'score': preference_score * 0.8,  # Base score for category match
                        'type': 'content_based',
                        'algorithm': 'category_based',
                        'metadata': {
                            'category_id': category_id,
                            'preference_score': preference_score
                        }
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in content-based filtering: {e}")
            return []
    
    def _trending_products(self) -> List[Dict[str, Any]]:
        """Get trending products based on recent activity"""
        try:
            from products.models import Product
            from django.db.models import Count, Q
            from datetime import timedelta
            
            # Get products with high activity in the last 7 days
            week_ago = timezone.now() - timedelta(days=7)
            
            trending_products = Product.objects.filter(
                is_active=True,
                behaviors__created_at__gte=week_ago
            ).annotate(
                activity_count=Count('behaviors', filter=Q(behaviors__created_at__gte=week_ago))
            ).order_by('-activity_count')[:20]
            
            recommendations = []
            max_activity = max([p.activity_count for p in trending_products], default=1)
            
            for product in trending_products:
                # Normalize score based on activity
                score = min(product.activity_count / max_activity, 1.0)
                
                recommendations.append({
                    'product': product,
                    'score': score * 0.7,  # Lower weight for trending
                    'type': 'trending',
                    'algorithm': 'trending_analysis',
                    'metadata': {
                        'activity_count': product.activity_count,
                        'time_period': '7_days'
                    }
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in trending products: {e}")
            return []
    
    def _similar_products(self, user: User) -> List[Dict[str, Any]]:
        """Find products similar to user's recent purchases"""
        try:
            # Get user's recent purchases
            recent_purchases = UserBehavior.objects.filter(
                user=user,
                behavior_type='purchase',
                product__isnull=False
            ).order_by('-created_at')[:5]
            
            if not recent_purchases:
                return []
            
            recommendations = []
            user_product_ids = set(p.product_id for p in recent_purchases)
            
            for purchase in recent_purchases:
                # Find similar products based on category and price range
                similar_products = self._find_similar_products(purchase.product)
                
                for product, similarity_score in similar_products:
                    if product.id not in user_product_ids:
                        recommendations.append({
                            'product': product,
                            'score': similarity_score * 0.6,
                            'type': 'similar',
                            'algorithm': 'product_similarity',
                            'metadata': {
                                'based_on_product': purchase.product.id,
                                'similarity_score': similarity_score
                            }
                        })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in similar products: {e}")
            return []
    
    def _frequently_bought_together(self, user: User) -> List[Dict[str, Any]]:
        """Find products frequently bought together with user's purchases"""
        try:
            # Get user's purchase history
            user_purchases = UserBehavior.objects.filter(
                user=user,
                behavior_type='purchase',
                product__isnull=False
            ).values_list('product_id', flat=True)
            
            if len(user_purchases) < 2:
                return []
            
            # Find products frequently bought together
            from orders.models import OrderItem
            from django.db.models import Count
            
            # Get orders that contain user's purchased products
            related_orders = OrderItem.objects.filter(
                product_id__in=user_purchases
            ).values_list('order_id', flat=True).distinct()
            
            # Find other products in those orders
            frequently_bought = OrderItem.objects.filter(
                order_id__in=related_orders
            ).exclude(product_id__in=user_purchases).values('product').annotate(
                frequency=Count('product')
            ).order_by('-frequency')[:10]
            
            recommendations = []
            max_frequency = max([item['frequency'] for item in frequently_bought], default=1)
            
            for item in frequently_bought:
                from products.models import Product
                try:
                    product = Product.objects.get(id=item['product'])
                    score = item['frequency'] / max_frequency
                    
                    recommendations.append({
                        'product': product,
                        'score': score * 0.5,
                        'type': 'frequently_bought',
                        'algorithm': 'market_basket_analysis',
                        'metadata': {
                            'frequency': item['frequency'],
                            'based_on_orders': len(related_orders)
                        }
                    })
                except Product.DoesNotExist:
                    continue
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in frequently bought together: {e}")
            return []
    
    def _find_similar_users(self, user: User, limit: int = 10) -> List[tuple]:
        """Find users with similar behavior patterns"""
        try:
            # Get user's behavior profile
            user_behaviors = UserBehavior.objects.filter(user=user)
            user_profile = defaultdict(float)
            
            for behavior in user_behaviors:
                if behavior.product:
                    user_profile[f"product_{behavior.product_id}"] += behavior.value
                if behavior.category:
                    user_profile[f"category_{behavior.category_id}"] += behavior.value
            
            if not user_profile:
                return []
            
            # Find similar users
            similar_users = []
            all_users = User.objects.exclude(id=user.id)
            
            for other_user in all_users:
                other_behaviors = UserBehavior.objects.filter(user=other_user)
                other_profile = defaultdict(float)
                
                for behavior in other_behaviors:
                    if behavior.product:
                        other_profile[f"product_{behavior.product_id}"] += behavior.value
                    if behavior.category:
                        other_profile[f"category_{behavior.category_id}"] += behavior.value
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(user_profile, other_profile)
                if similarity > 0.1:  # Minimum similarity threshold
                    similar_users.append((other_user, similarity))
            
            # Sort by similarity and return top users
            similar_users.sort(key=lambda x: x[1], reverse=True)
            return similar_users[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar users: {e}")
            return []
    
    def _get_user_preferences(self, user: User) -> Dict[str, Any]:
        """Get user preferences based on behavior history"""
        try:
            preferences = {
                'categories': defaultdict(float),
                'price_range': {'min': 0, 'max': 0},
                'brands': defaultdict(float)
            }
            
            behaviors = UserBehavior.objects.filter(user=user)
            
            for behavior in behaviors:
                if behavior.category:
                    preferences['categories'][behavior.category_id] += behavior.value
                
                if behavior.product:
                    # Track price preferences
                    if behavior.product.price:
                        if preferences['price_range']['min'] == 0:
                            preferences['price_range']['min'] = behavior.product.price
                            preferences['price_range']['max'] = behavior.product.price
                        else:
                            preferences['price_range']['min'] = min(preferences['price_range']['min'], behavior.product.price)
                            preferences['price_range']['max'] = max(preferences['price_range']['max'], behavior.product.price)
                    
                    # Track brand preferences
                    if behavior.product.seller:
                        preferences['brands'][behavior.product.seller.name] += behavior.value
            
            # Normalize preferences
            if preferences['categories']:
                max_cat_score = max(preferences['categories'].values())
                for cat_id in preferences['categories']:
                    preferences['categories'][cat_id] /= max_cat_score
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    def _find_similar_products(self, product, limit: int = 5) -> List[tuple]:
        """Find products similar to the given product"""
        try:
            from products.models import Product
            
            # Find products in same category with similar price
            similar_products = Product.objects.filter(
                category=product.category,
                is_active=True
            ).exclude(id=product.id)
            
            # Calculate similarity scores
            similarities = []
            for similar_product in similar_products:
                score = self._calculate_product_similarity(product, similar_product)
                if score > 0.3:  # Minimum similarity threshold
                    similarities.append((similar_product, score))
            
            # Sort by similarity and return top products
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error finding similar products: {e}")
            return []
    
    def _calculate_product_similarity(self, product1, product2) -> float:
        """Calculate similarity between two products"""
        try:
            score = 0.0
            
            # Category similarity (40% weight)
            if product1.category == product2.category:
                score += 0.4
            
            # Price similarity (30% weight)
            if product1.price and product2.price:
                price_diff = abs(product1.price - product2.price)
                max_price = max(product1.price, product2.price)
                if max_price > 0:
                    price_similarity = 1 - (price_diff / max_price)
                    score += price_similarity * 0.3
            
            # Seller similarity (20% weight)
            if product1.seller == product2.seller:
                score += 0.2
            
            # Title similarity (10% weight)
            title_similarity = self._text_similarity(product1.title, product2.title)
            score += title_similarity * 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating product similarity: {e}")
            return 0.0
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using simple word overlap"""
        try:
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union) if union else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0
    
    def _cosine_similarity(self, profile1: Dict, profile2: Dict) -> float:
        """Calculate cosine similarity between two profiles"""
        try:
            # Get all unique keys
            all_keys = set(profile1.keys()).union(set(profile2.keys()))
            
            if not all_keys:
                return 0.0
            
            # Calculate dot product and magnitudes
            dot_product = sum(profile1.get(key, 0) * profile2.get(key, 0) for key in all_keys)
            magnitude1 = math.sqrt(sum(profile1.get(key, 0) ** 2 for key in all_keys))
            magnitude2 = math.sqrt(sum(profile2.get(key, 0) ** 2 for key in all_keys))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def _deduplicate_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate recommendations and combine scores"""
        product_scores = defaultdict(list)
        
        for rec in recommendations:
            product_id = rec['product'].id
            product_scores[product_id].append(rec)
        
        # Combine scores for duplicate products
        unique_recommendations = []
        for product_id, recs in product_scores.items():
            if len(recs) == 1:
                unique_recommendations.append(recs[0])
            else:
                # Combine scores using weighted average
                total_score = sum(rec['score'] for rec in recs)
                combined_metadata = {}
                for rec in recs:
                    combined_metadata.update(rec.get('metadata', {}))
                
                unique_recommendations.append({
                    'product': recs[0]['product'],
                    'score': total_score / len(recs),  # Average score
                    'type': 'hybrid',
                    'algorithm': 'combined',
                    'metadata': combined_metadata
                })
        
        return unique_recommendations
    
    def _store_recommendations(self, user: User, recommendations: List[Dict[str, Any]]):
        """Store recommendations in database"""
        try:
            # Clear expired recommendations
            ProductRecommendation.objects.filter(
                user=user,
                expires_at__lt=timezone.now()
            ).delete()
            
            # Store new recommendations
            for rec in recommendations:
                ProductRecommendation.objects.update_or_create(
                    user=user,
                    product=rec['product'],
                    recommendation_type=rec['type'],
                    defaults={
                        'score': rec['score'],
                        'algorithm': rec['algorithm'],
                        'metadata': rec.get('metadata', {}),
                        'expires_at': timezone.now() + timezone.timedelta(hours=24)
                    }
                )
                
        except Exception as e:
            logger.error(f"Error storing recommendations: {e}")
    
    def track_user_behavior(self, user: User, behavior_type: str, 
                          product=None, category=None, value: float = 1.0, 
                          metadata: Dict = None, session_id: str = None,
                          request=None):
        """Track user behavior for recommendation learning"""
        try:
            behavior = UserBehavior.objects.create(
                user=user,
                behavior_type=behavior_type,
                product=product,
                category=category,
                value=value,
                metadata=metadata or {},
                session_id=session_id or '',
                ip_address=request.META.get('REMOTE_ADDR') if request else None,
                user_agent=request.META.get('HTTP_USER_AGENT', '') if request else ''
            )
            
            # Invalidate user's recommendation cache
            cache_pattern = f"recommendations:{user.id}:*"
            if hasattr(cache, 'delete_pattern'):
                cache.delete_pattern(cache_pattern)
            
            logger.info(f"Tracked behavior: {user.phone} - {behavior_type}")
            return behavior
            
        except Exception as e:
            logger.error(f"Error tracking user behavior: {e}")
            return None

# Global recommendation engine instance
recommendation_engine = RecommendationEngine()
