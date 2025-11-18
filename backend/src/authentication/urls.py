from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import RegisterView, login_view, MeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', login_view, name='auth-login'),
    path('refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
]
