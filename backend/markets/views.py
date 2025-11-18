# backend/markets/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import yfinance as yf # Required: 'pip install yfinance' 

class LiveStockPricesAPIView(APIView):
    """
    Fetches real-time stock price data for a list of specified tickers.
    Tickers are passed via the 'tickers' GET query parameter as a comma-separated string.
    """
    def get(self, request, *args, **kwargs):
        # 1. Retrieve the comma-separated ticker list from the request query parameters
        # Example: ?tickers=AAPL,GOOGL,MSFT
        tickers_param = request.query_params.get('tickers')
        if not tickers_param:
            return Response({"error": "No tickers provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Sanitize and normalize the list of tickers
        ticker_list = [t.strip().upper() for t in tickers_param.split(',')]
        
        # Use yfinance.Tickers to fetch data for multiple symbols simultaneously
        try:
            data = yf.Tickers(ticker_list).tickers
        except Exception as e:
            # Handle rate limiting or general yfinance errors gracefully
            print(f"yfinance error: {e}")
            return Response({"error": "Failed to fetch stock data due to external API issue."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        results = []
        for ticker_symbol, ticker_obj in data.items():
            try:
                # Get the core information dictionary
                info = ticker_obj.info
                
                # Extract necessary fields for the stock card
                current_price = info.get('currentPrice')
                previous_close = info.get('previousClose')
                
                change_amount = None
                change_percent = None
                
                # Calculate change amount and percentage
                if current_price and previous_close:
                    change_amount = current_price - previous_close
                    # Avoid division by zero
                    if previous_close != 0:
                        change_percent = (change_amount / previous_close) * 100
                    else:
                        change_percent = 0 # No change if previous close was 0 (unlikely for active stocks)
                
                results.append({
                    "symbol": ticker_symbol,
                    "name": info.get('shortName', ticker_symbol),
                    "price": current_price,
                    "changeAmount": change_amount,
                    "changePercent": change_percent,
                    # Add other relevant info like 'marketCap', 'sector' if needed
                })
            except Exception as e:
                # Handle error for a specific, invalid ticker
                print(f"Error processing ticker {ticker_symbol}: {e}")
                results.append({"symbol": ticker_symbol, "error": "Data not available."})

        return Response(results, status=status.HTTP_200_OK)