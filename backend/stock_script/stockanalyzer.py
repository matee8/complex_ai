import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import statistics

# ---------- CONFIGURATION ----------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

# ---------- DATA FETCHING ----------
def fetch_all_companies() -> List[Dict]:
    """Return only selected companies"""
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

    # You can fetch from Supabase individually OR just return minimal objects.
    companies = []
    for sym in symbols:
        companies.append({"symbol": sym, "name": sym})  
    return companies


def fetch_stock_history(symbol: str, days: int = 7) -> List[Dict]:
    """Get price history for a stock"""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/quotes?symbol=eq.{symbol}&created_at=gte.{cutoff}&select=*&order=created_at",
        headers=HEADERS
    )
    return response.json()

def fetch_fundamentals(symbol: str) -> Dict:
    """Get fundamental metrics for a stock"""
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/fundamentals?symbol=eq.{symbol}&select=*",
        headers=HEADERS
    )
    data = response.json()
    return data[0] if data else {}

# ---------- TECHNICAL ANALYSIS ----------
class TechnicalAnalyzer:
    """Calculate technical indicators"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index (0-100)"""
        if len(prices) < period + 1:
            return 50  # Neutral if not enough data
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_momentum(prices: List[float], days: int = 5) -> float:
        """Calculate price momentum (% change over period)"""
        if len(prices) < days:
            return 0
        
        old_price = prices[-days]
        current_price = prices[-1]
        
        if old_price == 0:
            return 0
        
        return ((current_price - old_price) / old_price) * 100
    
    @staticmethod
    def calculate_volatility(prices: List[float]) -> float:
        """Calculate price volatility (standard deviation)"""
        if len(prices) < 2:
            return 0
        
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        return statistics.stdev(returns) if returns else 0
    
    @staticmethod
    def moving_average(prices: List[float], period: int) -> float:
        """Calculate simple moving average"""
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        return sum(prices[-period:]) / period

# ---------- FUNDAMENTAL ANALYSIS ----------
class FundamentalAnalyzer:
    """Analyze fundamental metrics"""
    
    @staticmethod
    def get_pe_ratio(fundamentals: Dict) -> float:
        """Get P/E ratio"""
        try:
            metrics = fundamentals.get('metrics', {}).get('metric', {})
            pe = metrics.get('peBasicExclExtraTTM') or metrics.get('peNormalizedAnnual')
            return float(pe) if pe else 0
        except:
            return 0
    
    @staticmethod
    def get_eps(fundamentals: Dict) -> float:
        """Get Earnings Per Share"""
        try:
            metrics = fundamentals.get('metrics', {}).get('metric', {})
            eps = metrics.get('epsExclExtraItemsTTM') or metrics.get('epsTTM')
            return float(eps) if eps else 0
        except:
            return 0
    
    @staticmethod
    def get_52w_high_low(fundamentals: Dict) -> Tuple[float, float]:
        """Get 52-week high and low"""
        try:
            metrics = fundamentals.get('metrics', {}).get('metric', {})
            high = float(metrics.get('52WeekHigh', 0))
            low = float(metrics.get('52WeekLow', 0))
            return high, low
        except:
            return 0, 0

# ---------- SCORING SYSTEM ----------
class StockScorer:
    """Score stocks based on multiple factors"""
    
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
        self.fundamental_analyzer = FundamentalAnalyzer()
    
    def score_stock(self, company: Dict, history: List[Dict], fundamentals: Dict) -> Dict:
        """Calculate comprehensive score for a stock"""
        
        prices = [h['current_price'] for h in history if h.get('current_price')]
        
        if not prices or len(prices) < 3:
            return {
            'symbol': company['symbol'],
            'name': company.get('name', 'N/A'),
            'current_price': prices[-1] if prices else None,
            'score': 0,
            'recommendation': "🔴 AVOID",
            'action': "Insufficient data",
            'reasons': ["Not enough price history"],
            'signals': {},
            'metrics': {}
            }

        
        # Technical indicators
        rsi = self.analyzer.calculate_rsi(prices)
        momentum = self.analyzer.calculate_momentum(prices, days=5)
        volatility = self.analyzer.calculate_volatility(prices)
        ma_5 = self.analyzer.moving_average(prices, 5)
        current_price = prices[-1]
        
        # Fundamental metrics
        pe_ratio = self.fundamental_analyzer.get_pe_ratio(fundamentals)
        eps = self.fundamental_analyzer.get_eps(fundamentals)
        high_52w, low_52w = self.fundamental_analyzer.get_52w_high_low(fundamentals)
        
        # Initialize score
        score = 50  # Start neutral
        signals = {}
        reasons = []
        
        # RSI Signal (30 points)
        if rsi < 30:
            score += 15
            signals['rsi'] = 'OVERSOLD - Strong Buy'
            reasons.append(f"Oversold (RSI: {rsi:.1f})")
        elif rsi < 40:
            score += 8
            signals['rsi'] = 'Undervalued'
            reasons.append(f"Undervalued (RSI: {rsi:.1f})")
        elif rsi > 70:
            score -= 15
            signals['rsi'] = 'OVERBOUGHT - Avoid'
            reasons.append(f"Overbought (RSI: {rsi:.1f})")
        else:
            signals['rsi'] = 'Neutral'
        
        # Momentum Signal (20 points)
        if momentum > 5:
            score += 10
            signals['momentum'] = 'Strong uptrend'
            reasons.append(f"Strong momentum (+{momentum:.1f}%)")
        elif momentum > 2:
            score += 5
            signals['momentum'] = 'Uptrend'
            reasons.append(f"Positive trend (+{momentum:.1f}%)")
        elif momentum < -5:
            score -= 10
            signals['momentum'] = 'Downtrend'
            reasons.append(f"Declining (-{abs(momentum):.1f}%)")
        else:
            signals['momentum'] = 'Stable'
        
        # Price vs Moving Average (15 points)
        if current_price < ma_5 * 0.98:
            score += 8
            signals['price_ma'] = 'Below MA - Dip opportunity'
            reasons.append("Trading below average (buy dip)")
        elif current_price > ma_5 * 1.02:
            score -= 5
            signals['price_ma'] = 'Above MA - Hot'
        else:
            signals['price_ma'] = 'Near MA'
        
        # Volatility (10 points) - lower is better for safety
        if volatility < 0.02:
            score += 5
            signals['volatility'] = 'Low risk'
        elif volatility > 0.05:
            score -= 5
            signals['volatility'] = 'High risk'
            reasons.append("High volatility - risky")
        else:
            signals['volatility'] = 'Medium risk'
        
        # P/E Ratio (15 points)
        if 0 < pe_ratio < 15:
            score += 10
            signals['pe'] = 'Undervalued P/E'
            reasons.append(f"Low P/E ratio ({pe_ratio:.1f})")
        elif 15 <= pe_ratio <= 25:
            score += 5
            signals['pe'] = 'Fair P/E'
        elif pe_ratio > 40:
            score -= 8
            signals['pe'] = 'Overvalued P/E'
            reasons.append(f"High P/E ({pe_ratio:.1f})")
        else:
            signals['pe'] = 'P/E unavailable'
        
        # 52-week position (10 points)
        if high_52w > 0 and low_52w > 0:
            position = (current_price - low_52w) / (high_52w - low_52w)
            if position < 0.3:
                score += 8
                signals['52w'] = 'Near 52w low - opportunity'
                reasons.append("Near yearly low")
            elif position > 0.8:
                score -= 5
                signals['52w'] = 'Near 52w high'
        
        # Cap score at 0-100
        score = max(0, min(100, score))
        
        # Recommendation
        if score >= 75:
            recommendation = "🟢 STRONG BUY"
            action = "Excellent opportunity"
        elif score >= 60:
            recommendation = "🟢 BUY"
            action = "Good opportunity"
        elif score >= 45:
            recommendation = "⚪ HOLD"
            action = "Monitor for entry"
        elif score >= 30:
            recommendation = "🟡 CAUTION"
            action = "Wait for better entry"
        else:
            recommendation = "🔴 AVOID"
            action = "Not recommended"
        
        return {
            'symbol': company['symbol'],
            'name': company.get('name', 'N/A'),
            'current_price': current_price,
            'score': score,
            'recommendation': recommendation,
            'action': action,
            'reasons': reasons,
            'signals': signals,
            'metrics': {
                'rsi': round(rsi, 1),
                'momentum': round(momentum, 2),
                'volatility': round(volatility * 100, 2),
                'pe_ratio': round(pe_ratio, 1) if pe_ratio else 'N/A',
                'current_vs_ma': round((current_price / ma_5 - 1) * 100, 2) if ma_5 else 0
            }
        }

# ---------- MAIN RECOMMENDER ----------
class StockRecommender:
    """Main recommendation engine"""
    
    def __init__(self):
        self.scorer = StockScorer()
    
    def analyze_all_stocks(self) -> List[Dict]:
        """Analyze all stocks and return recommendations"""
        print("🔍 Analyzing stocks...")
        
        companies = fetch_all_companies()
        recommendations = []
        
        for company in companies:
            symbol = company['symbol']
            print(f"  Analyzing {symbol}...", end=" ")
            
            # Get historical data
            history = fetch_stock_history(symbol, days=14)
            fundamentals = fetch_fundamentals(symbol)
            
            if not history:
                print("⚠️ No data")
                continue
            
            # Score the stock
            result = self.scorer.score_stock(company, history, fundamentals)
            recommendations.append(result)
            print(f"{result['recommendation']}")
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
    
    def print_recommendations(self, recommendations: List[Dict], top_n: int = 10):
        """Print formatted recommendations"""
        print("\n" + "="*80)
        print("📊 STOCK RECOMMENDATIONS - TOP PICKS")
        print("="*80)
        
        for i, rec in enumerate(recommendations[:top_n], 1):
            print(f"\n{i}. {rec['recommendation']} {rec['symbol']} - {rec['name']}")
            print(f"   Score: {rec['score']}/100 | Price: ${rec['current_price']:.2f} | {rec['action']}")
            
            if rec['reasons']:
                print(f"   Why: {', '.join(rec['reasons'])}")
            
            print(f"   Metrics: RSI={rec['metrics']['rsi']}, "
                  f"Momentum={rec['metrics']['momentum']:+.2f}%, "
                  f"P/E={rec['metrics']['pe_ratio']}")
        
        print("\n" + "="*80)
        
        # Summary statistics
        buy_signals = sum(1 for r in recommendations if r['score'] >= 60)
        avoid_signals = sum(1 for r in recommendations if r['score'] < 30)
        
        print(f"\n📈 Summary:")
        print(f"   Buy Recommendations: {buy_signals}")
        print(f"   Hold/Monitor: {len(recommendations) - buy_signals - avoid_signals}")
        print(f"   Avoid: {avoid_signals}")
        print(f"   Average Score: {sum(r['score'] for r in recommendations) / len(recommendations):.1f}/100")
    
    def get_top_picks(self, recommendations: List[Dict], count: int = 3) -> List[Dict]:
        """Get top N stock picks"""
        return recommendations[:count]
    
    def create_portfolio_suggestion(self, recommendations: List[Dict], budget: float = 10000):
        """Suggest a diversified portfolio"""
        print("\n" + "="*80)
        print(f"💼 SUGGESTED PORTFOLIO (Budget: ${budget:,.0f})")
        print("="*80)
        
        # Get top stocks with score >= 60
        top_stocks = [r for r in recommendations if r['score'] >= 60][:5]
        
        if not top_stocks:
            print("❌ No strong buy signals at this time. Consider waiting.")
            return
        
        # Equal weight allocation
        allocation = budget / len(top_stocks)
        
        total_cost = 0
        for stock in top_stocks:
            shares = int(allocation / stock['current_price'])
            cost = shares * stock['current_price']
            total_cost += cost
            percentage = (cost / budget) * 100
            
            print(f"\n{stock['symbol']:6} - {stock['name'][:30]:30}")
            print(f"   Buy: {shares} shares @ ${stock['current_price']:.2f}")
            print(f"   Cost: ${cost:,.2f} ({percentage:.1f}% of portfolio)")
            print(f"   Score: {stock['score']}/100")
        
        print(f"\nTotal Invested: ${total_cost:,.2f}")
        print(f"Cash Remaining: ${budget - total_cost:,.2f}")
        print("="*80)

# ---------- MAIN ----------
def main():
    print("="*80)
    print("🤖 AI STOCK RECOMMENDATION SYSTEM")
    print("="*80)
    
    recommender = StockRecommender()
    
    # Analyze all stocks
    recommendations = recommender.analyze_all_stocks()
    
    # Print top recommendations
    recommender.print_recommendations(recommendations, top_n=10)
    
    # Suggest portfolio
    recommender.create_portfolio_suggestion(recommendations, budget=10000)
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()