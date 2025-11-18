# backend/src/complex_ai/urls.py (Example structure)

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Backend is running successfully!")

urlpatterns = [
    path('admin/', admin.site.urls),
    # Existing authentication URLs
    path('api/auth/', include('authentication.urls')),
    path('', home),  
    # Include markets app URLs (NEW)
    path('api/markets/', include('markets.urls')), 
]
