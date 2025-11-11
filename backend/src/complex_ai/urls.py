# backend/src/complex_ai/urls.py (Example structure)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Existing authentication URLs
    path('api/auth/', include('authentication.urls')),
    
    # Include markets app URLs (NEW)
    path('api/markets/', include('markets.urls')), 
]