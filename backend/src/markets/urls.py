# backend/markets/urls.py

from django.urls import path
from .views import LiveStockPricesAPIView

urlpatterns = [
    path('live-prices/', LiveStockPricesAPIView.as_view(), name='live-prices'),
]