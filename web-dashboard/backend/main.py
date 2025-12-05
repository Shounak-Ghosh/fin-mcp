from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import uvicorn
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.environ.get("OPENAI_API_KEY")
client = None
if api_key:
    client = OpenAI(api_key=api_key)
else:
    print("Warning: OPENAI_API_KEY not found. AI summary feature will be disabled.")

import random
import time

# Shared Cache System
PRICE_CACHE = {}
PRICE_CACHE_DURATION = 30  # 30 seconds (Balanced to safe-guard against rate limits)

HISTORY_CACHE = {}
HISTORY_CACHE_DURATION = 60  # 60 seconds (Much faster updates for graphs)

AI_SUMMARY_CACHE = {
    "timestamp": 0,
    "summary": ""
}
AI_SUMMARY_CACHE_DURATION = 300  # 5 minutes

def get_cached_stock_data(symbol: str):
    """Fetch real-time price data with short-term caching"""
    current_time = time.time()
    
    # Check cache
    if symbol in PRICE_CACHE:
        cached = PRICE_CACHE[symbol]
        if current_time - cached["timestamp"] < PRICE_CACHE_DURATION:
            return cached["data"]

    try:
        ticker = yf.Ticker(symbol)
        fast_info = ticker.fast_info
        
        price = fast_info.last_price
        prev_close = fast_info.previous_close
        
        if price is not None and prev_close is not None:
            change = price - prev_close
            percent_change = (change / prev_close) * 100
            # Try to get a nice name
            name = ticker.info.get('shortName', ticker.info.get('longName', symbol))
        else:
            # Fallback
            price = 0.0
            change = 0.0
            percent_change = 0.0
            name = symbol

        # Sanity check
        if not isinstance(price, (int, float)):
             price = 0.0

        data = {
            "symbol": symbol,
            "name": name,
            "price": round(price, 2),
            "change": round(change, 2),
            "percentChange": round(percent_change, 2)
        }
        
        # Only cache if we got valid data
        if price > 0:
            PRICE_CACHE[symbol] = {
                "timestamp": current_time,
                "data": data
            }
        
        return data

    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        # Return stale data if available, or error placeholder
        if symbol in PRICE_CACHE:
            return PRICE_CACHE[symbol]["data"]
        return {
            "symbol": symbol,
            "name": symbol,
            "price": 0.0,
            "change": 0.0,
            "percentChange": 0.0
        }

def get_cached_history(symbol: str):
    """Fetch 5-day history with long-term caching"""
    current_time = time.time()
    
    if symbol in HISTORY_CACHE:
        cached = HISTORY_CACHE[symbol]
        if current_time - cached["timestamp"] < HISTORY_CACHE_DURATION:
            return cached["data"]
            
    try:
        ticker = yf.Ticker(symbol)
        # Get 5 day history to ensure we cover the last 24 hours
        history_df = ticker.history(period="5d", interval="15m", prepost=True)
        
        history_data = []
        if not history_df.empty:
            # Filter for last 24 hours
            import pandas as pd
            from datetime import timedelta
            
            last_time = history_df.index[-1]
            cutoff_time = last_time - timedelta(hours=24)
            
            filtered_df = history_df[history_df.index > cutoff_time]
            
            for time_idx, row in filtered_df.iterrows():
                history_data.append({
                    "time": time_idx.isoformat(),
                    "value": round(row['Close'], 4)
                })
        
        # Fallback if empty
        if not history_data:
             # Need a price to mock a flat line?
             # We can't easily get price here without recursion, so just return empty or minimal
             # The frontend handles empty arrays? Or we can fetch price just for this.
             pass

        HISTORY_CACHE[symbol] = {
            "timestamp": current_time,
            "data": history_data
        }
        return history_data

    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        if symbol in HISTORY_CACHE:
            return HISTORY_CACHE[symbol]["data"]
        return []

@app.get("/api/market-status")
def get_market_status():
    # Load watchlist symbols to determine what to show
    symbols = load_watchlist_symbols()
    
    # Default logic
    default_tickers = ["ES=F", "NQ=F", "YM=F", "^VIX"]
    target_symbols = []
    
    if not symbols:
        target_symbols = default_tickers
    else:
        # Take up to 4 from watchlist
        target_symbols = symbols[:4]
        # Fill remainder with defaults if needed
        if len(target_symbols) < 4:
            for ticker in default_tickers:
                if ticker not in target_symbols:
                    target_symbols.append(ticker)
                    if len(target_symbols) >= 4:
                        break
    
    results = []
    for symbol in target_symbols:
        # 1. Get Price Data
        price_data = get_cached_stock_data(symbol)
        
        # 2. Get History Data (only needed for these sparkline cards)
        history_data = get_cached_history(symbol)
        
        # 3. If history is empty, assume flat line based on current price
        if not history_data and price_data["price"] > 0:
             history_data = [
                 {"time": "2024-01-01T00:00:00", "value": price_data["price"]},
                 {"time": "2024-01-01T23:59:59", "value": price_data["price"]}
             ]
             
        # Combine
        full_data = price_data.copy()
        full_data["history"] = history_data
        
        results.append(full_data)
            
    return results

import json
import requests
from pydantic import BaseModel

WATCHLIST_FILE = "watchlist.json"

def load_watchlist_symbols():
    if not os.path.exists(WATCHLIST_FILE):
        return []
    with open(WATCHLIST_FILE, "r") as f:
        return json.load(f)

def save_watchlist_symbols(symbols):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(symbols, f)

class WatchlistAddRequest(BaseModel):
    symbol: str

@app.get("/api/watchlist")
def get_watchlist():
    symbols = load_watchlist_symbols()
    if not symbols:
        return []
        
    results = []
    for symbol in symbols:
        # Use simple shared cache
        price_data = get_cached_stock_data(symbol)
        results.append(price_data)

    return results


@app.get("/api/search")
def search_stocks(q: str):
    results = []
    
    # 1. Try Yahoo Finance Search API
    try:
        # Try query1 instead of query2
        url = "https://query1.finance.yahoo.com/v1/finance/search"
        params = {
            "q": q,
            "quotesCount": 5,
            "newsCount": 0,
            "enableFuzzyQuery": "true",
            "quotesQueryId": "tss_match_phrase_query"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "quotes" in data:
                for quote in data["quotes"]:
                    if "symbol" in quote:
                        results.append({
                            "symbol": quote["symbol"],
                            "name": quote.get("shortname", quote.get("longname", quote["symbol"])),
                            "type": quote.get("quoteType", "Unknown"),
                            "exchange": quote.get("exchange", "")
                        })
    except Exception as e:
        print(f"Search API failed: {e}")

    # 2. Fallback: Check if 'q' is a valid ticker directly
    # Only if we have few results or API failed
    if len(results) == 0:
        try:
            # Check if it looks like a ticker
            if len(q) <= 6 and q.isalpha():
                ticker = yf.Ticker(q)
                # fast_info is cheap
                if ticker.fast_info.last_price:
                    info = ticker.info
                    results.append({
                        "symbol": q.upper(),
                        "name": info.get('shortName', info.get('longName', q.upper())),
                        "type": "Equity", # Assumption
                        "exchange": "Unknown"
                    })
        except Exception:
            pass
            
    return results

@app.post("/api/watchlist")
def add_to_watchlist(item: WatchlistAddRequest):
    symbols = load_watchlist_symbols()
    if item.symbol not in symbols:
        symbols.append(item.symbol)
        save_watchlist_symbols(symbols)
    return {"status": "success", "watchlist": symbols}

@app.delete("/api/watchlist/{symbol}")
def remove_from_watchlist(symbol: str):
    symbols = load_watchlist_symbols()
    if symbol in symbols:
        symbols.remove(symbol)
        save_watchlist_symbols(symbols)
    return {"status": "success", "watchlist": symbols}

@app.get("/api/news")
def get_news(limit: int = None):
    try:
        # Fetch news for a mix of indices and popular stocks to get a good market overview
        tickers = ["^GSPC", "^IXIC", "NVDA", "AAPL", "BTC-USD"]
        all_news = []
        
        seen_titles = set()

        for symbol in tickers:
            try:
                ticker = yf.Ticker(symbol)
                news_items = ticker.news
                
                for item in news_items:
                    # Handle different potential structures of yfinance news
                    content = item.get('content', item) # Sometimes it's nested, sometimes flat
                    
                    title = content.get('title')
                    if not title or title in seen_titles:
                        continue
                    
                    seen_titles.add(title)
                    
                    # Extract URL
                    url = ""
                    if 'clickThroughUrl' in content and content['clickThroughUrl']:
                         url = content['clickThroughUrl'].get('url', '')
                    elif 'link' in content:
                        url = content['link']
                    
                    # Extract Publisher
                    source = "Yahoo Finance"
                    if 'provider' in content and content['provider']:
                        source = content['provider'].get('displayName', source)
                        
                    # Extract Time
                    pub_date = content.get('pubDate', '')
                    # Simple formatting or just pass through. 
                    # Frontend might expect "Updated X hours ago", but for now let's pass the date string
                    # Or we can try to parse it. yfinance usually gives ISO format.
                    
                    all_news.append({
                        "title": title,
                        "summary": content.get('summary', title), # Use title as fallback summary
                        "source": source,
                        "time": pub_date, # Passing raw date for now, frontend might need adjustment or we format here
                        "url": url
                    })
            except Exception as e:
                print(f"Error fetching news for {symbol}: {e}")
                continue

        # Sort by time (descending) if possible, or just shuffle/mix
        # yfinance news is usually recent.
        # Let's just return what we have, maybe limited
        
        if not all_news:
             # Fallback to mock data if no news found (e.g. rate limits or connection issues)
             return [
                {
                    "title": "Market data unavailable, showing cached news",
                    "summary": "Unable to fetch real-time news at the moment.",
                    "source": "System",
                    "time": "Now",
                    "url": "#"
                }
             ]

        if limit:
            return all_news[:limit]
        return all_news
        
    except Exception as e:
        print(f"Global error in get_news: {e}")
        return []

@app.get("/api/sectors")
def get_sectors():
    def fluctuate(value):
        return round(value + random.uniform(-0.1, 0.1), 2)

    return [
        {"name": "Technology", "value": fluctuate(291.09), "change": fluctuate(0.38)},
        {"name": "Energy", "value": fluctuate(92.26), "change": fluctuate(0.47)},
        {"name": "Discretionary", "value": fluctuate(238.18), "change": fluctuate(-0.34)},
        {"name": "Staples", "value": fluctuate(78.46), "change": fluctuate(-0.48)},
    ]

@app.get("/api/gainers")
def get_gainers():
    def fluctuate(value):
        return round(value + random.uniform(-1.0, 1.0), 2)

    return [
        {"symbol": "SMX", "name": "SMX (Security Matters) P...", "price": fluctuate(141.00), "change": fluctuate(141.07)},
        {"symbol": "PMI", "name": "Picard Medical, Inc.", "price": fluctuate(3.72), "change": fluctuate(84.11)},
    ]

@app.get("/api/ai-summary")
def get_ai_summary():
    try:
        # Check cache first
        current_time = time.time()
        if AI_SUMMARY_CACHE["summary"] and (current_time - AI_SUMMARY_CACHE["timestamp"] < AI_SUMMARY_CACHE_DURATION):
            return {"summary": AI_SUMMARY_CACHE["summary"]}

        # 1. Fetch Overall Market Indices (S&P 500, Nasdaq, Dow, VIX)
        indices_tickers = ["^GSPC", "^IXIC", "^DJI", "^VIX"]
        indices_data = []
        for symbol in indices_tickers:
            indices_data.append(get_cached_stock_data(symbol))

        # 2. Fetch User's Watchlist (First 4)
        watchlist_symbols = load_watchlist_symbols()[:4]
        watchlist_data = []
        for symbol in watchlist_symbols:
            watchlist_data.append(get_cached_stock_data(symbol))

        # Construct Prompt
        prompt = f"""
        Analyze the following market data and provide a response with exactly TWO distinct sections.

        Overall Market Summary
        - Analyze the "Market Indices" data below.
        - summarize the general market trend (bullish/bearish/mixed).
        - Mention key movements in S&P 500, Nasdaq, or Dow.

        Watchlist Summary
        - Analyze the "Your Watchlist" data below.
        - Provide a quick snapshot of how these specific stocks are performing.
        - Highlight the best or worst performer among them.

        Formatting Instructions:
        - Do NOT include "Section 1" or "Section 2" in the output. Just use the bold headers "**Overall Market Summary**" and "**Watchlist Summary**".
        - Separate the two sections with a double newline (\\n\\n).
        - Use **bold** for key terms and ticker symbols.
        - Use [[green|text]] for positive trends/gains.
        - Use [[red|text]] for negative trends/losses.
        - Use [[blue|text]] for neutral/highlights.
        - Keep the total response concise (approx 4-6 sentences total).

        data:
        
        Market Indices:
        {indices_data}
        
        Your Watchlist:
        {watchlist_data}
        """
        
        if not client:
            return {"summary": "AI Summary is unavailable (Missing OpenAI API Key). Please set OPENAI_API_KEY environment variable."}

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful financial analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=350
        )
        
        summary_text = response.choices[0].message.content.strip()
        
        # Update Cache
        AI_SUMMARY_CACHE["summary"] = summary_text
        AI_SUMMARY_CACHE["timestamp"] = current_time
        
        return {"summary": summary_text}
    except Exception as e:
        print(f"Error generating summary: {e}")
        # Return cached entry if available even if expired, as fallback
        if AI_SUMMARY_CACHE["summary"]:
             return {"summary": AI_SUMMARY_CACHE["summary"]}
        return {"summary": "Market is showing mixed signals today. Please check back later for a detailed AI analysis."}

@app.get("/api/stock/{symbol}/calculate")
def calculate_investment(symbol: str, date: str, amount: float):
    try:
        # Fetch historical data
        ticker = yf.Ticker(symbol)
        
        # Get historical data for the specific date
        # We ask for a small range around the date to handle weekends/holidays
        import pandas as pd
        from datetime import datetime, timedelta
        
        target_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = target_date - timedelta(days=5) # Look back a few days to find a trading day
        end_date = target_date + timedelta(days=1)
        
        history = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        
        if history.empty:
             return {
                "error": "No data found for this date. Please choose a recent past date."
            }
            
        # Get the closest available date <= target_date
        # history index is DatetimeIndex
        # We want the last row because that's the closest to our target date in the range we fetched
        initial_price = history['Close'].iloc[-1]
        actual_date = history.index[-1].strftime("%Y-%m-%d")
        
        # Get current price
        # fast_info is faster than history(period='1d')
        current_price = ticker.fast_info.last_price
        
        if not current_price:
             # Fallback
             current_data = ticker.history(period="1d")
             if not current_data.empty:
                 current_price = current_data['Close'].iloc[-1]
             else:
                 return {"error": "Could not fetch current price."}

        shares_bought = amount / initial_price
        current_value = shares_bought * current_price
        roi = ((current_value - amount) / amount) * 100
        
        return {
            "symbol": symbol,
            "initial_date": actual_date,
            "initial_price": round(initial_price, 2),
            "current_price": round(current_price, 2),
            "current_value": round(current_value, 2),
            "roi": round(roi, 2)
        }
        
    except Exception as e:
        print(f"Error calculating investment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}/history")
def get_stock_history(symbol: str, period: str = "1y"):
    try:
        ticker = yf.Ticker(symbol)
        
        # Determine interval based on period
        interval = "1d"
        if period == "1d":
            interval = "5m"
        elif period == "5d":
            interval = "30m" # 15m or 30m is good for 5d
        elif period == "1mo":
            interval = "90m" # 60m or 90m gives more detail than 1d
        
        # Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        history = ticker.history(period=period, interval=interval)
        
        if history.empty:
            return []
            
        # Format data for frontend
        data = []
        for date, row in history.iterrows():
            # For intraday intervals (anything less than 1d), date includes time
            # We should send the full ISO string so frontend can format it
            data.append({
                "date": date.isoformat(), 
                "price": round(row['Close'], 2)
            })
            
        return data
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
