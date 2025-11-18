from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from markets.services import get_live_prices


class LiveStockPricesAPIView(APIView):

    def get(self, request, *args, **kwargs):
        tickers_param = request.query_params.get('tickers')

        if not tickers_param:
            return Response({"error": "No tickers provided."},
                            status=status.HTTP_400_BAD_REQUEST)

        ticker_list = tickers_param.split(',')
        data = get_live_prices(ticker_list)

        if data and 'error' in data[0] and len(data) == 1:
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(data, status=status.HTTP_200_OK)
