from django.urls import path
from .views import SellerView, SellerDetailView

urlpatterns = [
    path('seller', SellerView.as_view(), name='seller-list'),
    path('seller/<int:id>', SellerDetailView.as_view(), name='seller-detail'),
]