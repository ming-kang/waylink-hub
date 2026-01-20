"""
URL configuration for waylink project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # API authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Apps URLs (to be created)
    path('api/auth/', include('apps.users.urls')),
    path('api/cabinets/', include('apps.cabinets.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/devices/', include('apps.devices.urls')),
    path('api/admin/', include('apps.operations.urls')),
]
