from rest_framework import serializers
from .models import Seller, Category, Product, Review
from accounts.models import CustomUser
from django.db.models import Avg, Count

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Review
        fields = ['product', 'user', 'product_rating']

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'product_number', 'is_active',
            'seller', 'category', 'price', 'discount_percentage', 'discounted_price',
            'slug', 'flash_sale', 'best_seller_product', 'featured_product',
            'average_rating', 'user_count', 'featured_image'
        ]

    def get_average_rating(self, obj):
        reviews = Review.objects.filter(product=obj)
        if reviews.exists():
            average_rating = reviews.aggregate(average_rating=Avg('product_rating'))['average_rating']
            return average_rating if average_rating is not None else 0
        return 0

    def get_user_count(self, obj):
        return Review.objects.filter(product=obj).values('user').distinct().count()
