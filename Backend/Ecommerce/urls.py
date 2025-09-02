
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from health_check import HealthCheckView, ReadinessCheckView, LivenessCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('accounts.urls') ),
    path('api/', include('products.urls') ),
    path('api/', include('orders.urls') ),
    path('api/', include('search.urls') ),
    
    # Health check endpoints
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('health/ready/', ReadinessCheckView.as_view(), name='readiness_check'),
    path('health/live/', LivenessCheckView.as_view(), name='liveness_check'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)