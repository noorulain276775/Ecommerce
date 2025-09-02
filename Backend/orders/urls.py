from django.urls import path
from .views import (
    CartView, CartItemView, OrderListCreateView, OrderDetailView,
    OrderStatusUpdateView, PaymentView, OrderAnalyticsView
)

urlpatterns = [
    # Cart endpoints
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/items/<int:item_id>/', CartItemView.as_view(), name='cart-item'),
    
    # Order endpoints
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<uuid:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/<uuid:order_id>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('orders/<uuid:order_id>/payment/', PaymentView.as_view(), name='order-payment'),
    
    # Analytics
    path('analytics/', OrderAnalyticsView.as_view(), name='order-analytics'),
]
