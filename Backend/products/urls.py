from django.urls import path
from .views import SellerView, SellerDetailView, CategoryView, CategoryDetailView, ProductDetailView, ProductView

urlpatterns = [
    path('sellers/', SellerView.as_view(), name='seller'),
    path('sellers/<int:id>/', SellerDetailView.as_view(), name='seller-detail'),
    path('categories/', CategoryView.as_view(), name='category'),
    path('categories/<int:id>', CategoryDetailView.as_view(), name='category-detail'),
    path('products/', ProductView.as_view(), name='product'),
    path('products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
]