import yfinance as yf
from typing import List, Dict, Any


def get_live_prices(tickers: List[str]) -> List[Dict[str, Any]]:
    """
    Fetches real-time stock data for a list of tickers using yfinance.
    """
    if not tickers:
        return []

    tickers = [t.strip().upper() for t in tickers if t.strip()]

    try:
        data = yf.Tickers(' '.join(tickers))
        results = []

        for symbol in tickers:
            try:
                ticker_obj = data.tickers[symbol]
                info = ticker_obj.info

                current_price = info.get('currentPrice')
                previous_close = info.get('previousClose')

                change_amount = None
                change_percent = None

                if current_price is not None and previous_close:
                    change_amount = current_price - previous_close
                    if previous_close != 0:
                        change_percent = (change_amount / previous_close) * 100
                    else:
                        change_percent = 0

                results.append({
                    "symbol": symbol,
                    "name": info.get('shortName', symbol),
                    "price": current_price,
                    "changeAmount": change_amount,
                    "changePercent": change_percent,
                })
            except Exception as e:
                results.append({"symbol": symbol, "error": "Data unavailable"})

        return results

    except Exception as e:
        print(f"yfinance error: {e}")
        return [{"error": "External API Unavailable"}]


def get_stock_prediction(symbol: str) -> Dict[str, Any]:
    """
    STUB: Future home of Neural Network + LLM logic.
    """

    return {
        "symbol": symbol,
        "prediction": "BULLISH",
        "confidence": 0.85,
        "ai_analysis": "Neural networks detect a strong momentum pattern..."
    }
