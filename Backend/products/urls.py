from django.urls import path
from .views import SellerView, SellerDetailView, CategoryView, CategoryDetailView, ProductDetailView, ProductView

urlpatterns = [
    path('seller', SellerView.as_view(), name='seller'),
    path('seller/<int:id>', SellerDetailView.as_view(), name='seller-detail'),
    path('category', CategoryView.as_view(), name='category'),
    path('category/<int:id>', CategoryDetailView.as_view(), name='category-detail'),
    path('product', ProductView.as_view(), name='product'),
    path('product/<int:id>', ProductDetailView.as_view(), name='product-detail'),
]