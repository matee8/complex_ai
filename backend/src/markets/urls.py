from django.urls import path

from markets.views import LiveStockPricesAPIView

urlpatterns = [
    path('live-prices/', LiveStockPricesAPIView.as_view(), name='live-prices'),
]
