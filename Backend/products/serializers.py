from rest_framework import serializers
from .models import Seller, Category, Product

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'product_number', 'is_active',
                  'seller', 'category', 'price', 'discount_percentage', 'discounted_price', 'slug']