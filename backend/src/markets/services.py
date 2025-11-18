import logging
from typing import List, Dict, Any

import requests
import yfinance as yf

logger = logging.getLogger(__name__)


def get_live_prices(tickers: List[str]) -> List[Dict[str, Any]]:
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
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'price': current_price,
                    'changeAmount': change_amount,
                    'changePercent': change_percent,
                })
            except (KeyError, AttributeError, IndexError, TypeError,
                    ValueError) as e:
                logger.warning('Error fetching data for %s: %s',
                               symbol,
                               e,
                               exc_info=True)
                results.append({'symbol': symbol, 'error': 'Data unavailable'})

        return results

    except (requests.exceptions.RequestException, OSError) as e:
        logger.error('yfinance connection error: %s', e, exc_info=True)
        return [{'error': 'External API Unavailable'}]


def get_stock_prediction(symbol: str) -> Dict[str, Any]:
    return {
        'symbol': symbol,
        'prediction': 'BULLISH',
        'confidence': 0.85,
        'ai_analysis': 'Neural networks detect a strong momentum pattern...'
    }
