import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple
import json

# ---------- CONFIGURATION ----------
load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# API Configuration
REQUEST_DELAY = 1.2
CONCURRENT_REQUESTS = 2
MAX_RETRIES = 2
REQUEST_TIMEOUT = 15

# Watchlist
WATCHLIST_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META"
]

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---------- SUPABASE REST CLIENT ----------
class SupabaseClient:
    """Simple Supabase REST API client - no dependencies!"""
    
    def __init__(self, url: str, key: str):
        self.base_url = f"{url}/rest/v1"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
    
    async def insert(self, table: str, data: List[Dict], session: aiohttp.ClientSession):
        """Insert data into table"""
        url = f"{self.base_url}/{table}"
        try:
            async with session.post(url, json=data, headers=self.headers) as resp:
                if resp.status in [200, 201]:
                    logger.info(f"✅ Inserted {len(data)} rows into {table}")
                    return True
                else:
                    text = await resp.text()
                    logger.error(f"Failed to insert into {table}: {resp.status} - {text}")
                    return False
        except Exception as e:
            logger.error(f"Error inserting into {table}: {e}")
            return False
    
    async def upsert(self, table: str, data: List[Dict], session: aiohttp.ClientSession):
        """Upsert data into table"""
        url = f"{self.base_url}/{table}"
        headers = {**self.headers, "Prefer": "resolution=merge-duplicates"}
        try:
            async with session.post(url, json=data, headers=headers) as resp:
                if resp.status in [200, 201]:
                    logger.info(f"✅ Upserted {len(data)} rows into {table}")
                    return True
                else:
                    text = await resp.text()
                    logger.error(f"Failed to upsert into {table}: {resp.status} - {text}")
                    return False
        except Exception as e:
            logger.error(f"Error upserting into {table}: {e}")
            return False
    
    async def select(self, table: str, session: aiohttp.ClientSession, filters: Dict = None):
        """Select data from table"""
        url = f"{self.base_url}/{table}"
        params = {}
        
        if filters:
            for key, value in filters.items():
                params[key] = f"eq.{value}"
        
        try:
            async with session.get(url, params=params, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f"Failed to select from {table}: {resp.status}")
                    return []
        except Exception as e:
            logger.error(f"Error selecting from {table}: {e}")
            return []

# ---------- FINNHUB CLIENT ----------
class FinnhubClient:
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
        self.request_count = 0
    
    async def _request(self, session: aiohttp.ClientSession, path: str, params: Dict = None) -> Tuple[Optional[Dict], Optional[str]]:
        if params is None:
            params = {}
        params["token"] = self.api_key
        url = f"{self.BASE_URL}{path}"
        
        async with self.semaphore:
            for attempt in range(MAX_RETRIES):
                try:
                    async with session.get(url, params=params, timeout=REQUEST_TIMEOUT) as resp:
                        self.request_count += 1
                        
                        if resp.status == 200:
                            data = await resp.json()
                            await asyncio.sleep(REQUEST_DELAY)
                            return data, None
                        elif resp.status == 429:
                            wait_time = REQUEST_DELAY * (2 ** attempt)
                            logger.warning(f"Rate limited. Waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                        else:
                            logger.warning(f"HTTP {resp.status} for {url}")
                            
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout on attempt {attempt+1} for {path}")
                except Exception as e:
                    logger.warning(f"Request failed: {str(e)}")
                
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(REQUEST_DELAY * (attempt + 1))
            
            return None, f"Failed after {MAX_RETRIES} attempts"
    
    async def fetch_profile(self, session: aiohttp.ClientSession, symbol: str) -> Tuple[Optional[Dict], Optional[str]]:
        return await self._request(session, "/stock/profile2", {"symbol": symbol})
    
    async def fetch_quote(self, session: aiohttp.ClientSession, symbol: str) -> Tuple[Optional[Dict], Optional[str]]:
        return await self._request(session, "/quote", {"symbol": symbol})
    
    async def fetch_fundamentals(self, session: aiohttp.ClientSession, symbol: str) -> Tuple[Optional[Dict], Optional[str]]:
        return await self._request(session, "/stock/metric", {"symbol": symbol, "metric": "all"})

# ---------- ORCHESTRATOR ----------
class StockOrchestrator:
    def __init__(self, finnhub: FinnhubClient, supabase: SupabaseClient):
        self.finnhub = finnhub
        self.supabase = supabase
    
    def process_profile(self, symbol: str, profile: Dict) -> Optional[Dict]:
        if not profile or not profile.get("name"):
            return None
        return {
            "symbol": symbol,
            "name": profile.get("name"),
            "exchange": profile.get("exchange"),
            "industry": profile.get("finnhubIndustry"),
            "marketcap": profile.get("marketCapitalization"),
            "country": profile.get("country"),
            "ipo": profile.get("ipo"),
            "weburl": profile.get("weburl"),
            "logo": profile.get("logo"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    def process_quote(self, symbol: str, quote: Dict) -> Optional[Dict]:
        if not quote or quote.get("c") is None:
            return None
        
        t_unix = quote.get("t")
        ts = datetime.fromtimestamp(int(t_unix), timezone.utc).isoformat() if t_unix else datetime.now(timezone.utc).isoformat()
        
        return {
            "symbol": symbol,
            "current_price": quote.get("c"),
            "high_price": quote.get("h"),
            "low_price": quote.get("l"),
            "open_price": quote.get("o"),
            "prev_close": quote.get("pc"),
            "change": quote.get("d"),
            "percent_change": quote.get("dp"),
            "timestamp": ts,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    def process_fundamentals(self, symbol: str, fundamentals: Dict) -> Optional[Dict]:
        if not fundamentals or "metric" not in fundamentals:
            return None
        return {
            "symbol": symbol,
            "metrics": fundamentals,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def fetch_stock_data(self, session: aiohttp.ClientSession, symbol: str):
        """Fetch all data for one stock"""
        logger.info(f"Processing {symbol}...")
        
        tasks = [
            self.finnhub.fetch_profile(session, symbol),
            self.finnhub.fetch_quote(session, symbol),
            self.finnhub.fetch_fundamentals(session, symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        profile_data, quote_data, fundamentals_data = None, None, None
        
        # Process profile
        if not isinstance(results[0], Exception):
            data, error = results[0]
            if not error and data:
                profile_data = self.process_profile(symbol, data)
        
        # Process quote
        if not isinstance(results[1], Exception):
            data, error = results[1]
            if not error and data:
                quote_data = self.process_quote(symbol, data)
        
        # Process fundamentals
        if not isinstance(results[2], Exception):
            data, error = results[2]
            if not error and data:
                fundamentals_data = self.process_fundamentals(symbol, data)
        
        return profile_data, quote_data, fundamentals_data
    
    async def ingest_watchlist(self, symbols: List[str]):
        """Ingest data for watchlist stocks"""
        logger.info(f"🚀 Starting ingestion for {len(symbols)} stocks")
        
        all_profiles = []
        all_quotes = []
        all_fundamentals = []
        
        async with aiohttp.ClientSession() as session:
            for i, symbol in enumerate(symbols, 1):
                logger.info(f"[{i}/{len(symbols)}] {symbol}")
                
                profile, quote, fundamentals = await self.fetch_stock_data(session, symbol)
                
                if profile:
                    all_profiles.append(profile)
                if quote:
                    all_quotes.append(quote)
                if fundamentals:
                    all_fundamentals.append(fundamentals)
            
            # Batch insert to database
            if all_profiles:
                await self.supabase.upsert("companies", all_profiles, session)
            if all_quotes:
                await self.supabase.insert("quotes", all_quotes, session)
            if all_fundamentals:
                await self.supabase.upsert("fundamentals", all_fundamentals, session)
        
        logger.info(f"✅ Ingestion complete!")
        logger.info(f"📈 API calls: {self.finnhub.request_count}")
        logger.info(f"💾 Profiles: {len(all_profiles)}, Quotes: {len(all_quotes)}, Fundamentals: {len(all_fundamentals)}")

# ---------- PORTFOLIO SUMMARY ----------
async def show_portfolio_summary(supabase: SupabaseClient):
    """Show portfolio summary"""
    logger.info("\n" + "="*60)
    logger.info("📊 PORTFOLIO SUMMARY")
    logger.info("="*60)
    
    async with aiohttp.ClientSession() as session:
        # Get companies
        companies = await supabase.select("companies", session)
        
        for company in companies[:10]:  # Show top 10
            symbol = company.get('symbol', 'N/A')
            name = company.get('name', 'N/A')[:25]
            
            # Get latest quote
            quotes = await supabase.select("quotes", session, {"symbol": symbol})
            
            if quotes:
                # Get most recent quote
                latest = sorted(quotes, key=lambda x: x.get('created_at', ''), reverse=True)[0]
                price = latest.get('current_price')
                change = latest.get('percent_change')
                
                if price and change is not None:
                    emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                    logger.info(f"{emoji} {symbol:6} | {name:25} | ${price:8.2f} | {change:+6.2f}%")
                else:
                    logger.info(f"⚪ {symbol:6} | {name:25} | No price data")
            else:
                logger.info(f"⚪ {symbol:6} | {name:25} | No quotes")
    
    logger.info("="*60 + "\n")

# ---------- MAIN ----------
async def main():
    logger.info("="*60)
    logger.info("📈 STOCK MARKET BOT")
    logger.info("="*60)
    
    finnhub = FinnhubClient(FINNHUB_API_KEY)
    supabase = SupabaseClient(SUPABASE_URL, SUPABASE_KEY)
    orchestrator = StockOrchestrator(finnhub, supabase)
    
    await orchestrator.ingest_watchlist(WATCHLIST_SYMBOLS)
    await show_portfolio_summary(supabase)

if __name__ == "__main__":
    asyncio.run(main())