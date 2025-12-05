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

# Simple cache: {symbol: {"data": data_dict, "timestamp": timestamp}}
MARKET_CACHE = {}
CACHE_DURATION = 60 # 60 seconds

@app.get("/api/market-status")
def get_market_status():
    global MARKET_CACHE
    current_time = time.time()
    
    # Load watchlist symbols
    symbols = load_watchlist_symbols()
    
    # Default to indices if watchlist is empty or has fewer than 4 items
    default_tickers = ["ES=F", "NQ=F", "YM=F", "^VIX"]
    if not symbols:
        target_symbols = default_tickers
    else:
        target_symbols = symbols[:4]
        # Fill with defaults if less than 4
        if len(target_symbols) < 4:
            for ticker in default_tickers:
                if ticker not in target_symbols:
                    target_symbols.append(ticker)
                    if len(target_symbols) >= 4:
                        break
    
    data = []
    
    for symbol in target_symbols:
        # Check cache
        if symbol in MARKET_CACHE:
            cached_data = MARKET_CACHE[symbol]
            if current_time - cached_data["timestamp"] < CACHE_DURATION:
                data.append(cached_data["data"])
                continue

        try:
            ticker = yf.Ticker(symbol)
            
            # Get current price info
            fast_info = ticker.fast_info
            price = fast_info.last_price
            prev_close = fast_info.previous_close
            
            if price is not None and prev_close is not None:
                change = price - prev_close
                percent_change = (change / prev_close) * 100
                name = ticker.info.get('shortName', symbol)
            else:
                # Fallback
                price = 0.0
                change = 0.0
                percent_change = 0.0
                name = symbol
            
            # Check for validity of price, sometimes yfinance returns broken objects
            if not isinstance(price, (int, float)):
                 price = 0.0
                 
            # Get 5 day history to ensure we cover the last 24 hours
            # 15m interval gives us enough detail without being too heavy
            history_df = ticker.history(period="5d", interval="15m", prepost=True)
            
            history_data = []
            if not history_df.empty:
                # Filter for last 24 hours
                import pandas as pd
                from datetime import timedelta
                
                # Get the last available timestamp
                last_time = history_df.index[-1]
                cutoff_time = last_time - timedelta(hours=24)
                
                filtered_df = history_df[history_df.index > cutoff_time]
                
                # Format data for frontend including time
                for time_idx, row in filtered_df.iterrows():
                    history_data.append({
                        "time": time_idx.isoformat(),
                        "value": round(row['Close'], 4)
                    })
            
            # If history is empty (e.g. market closed or error), mock flat line
            if not history_data:
                # Use current price
                 history_data = [
                     {"time": "2024-01-01T00:00:00", "value": price},
                     {"time": "2024-01-01T23:59:59", "value": price}
                 ]

            symbol_data = {
                "symbol": symbol,
                "name": name,
                "price": round(price, 2),
                "change": round(change, 2),
                "percentChange": round(percent_change, 2),
                "history": history_data
            }
            
            data.append(symbol_data)
            
            # Update cache if data looks valid (price > 0)
            if price > 0:
                 MARKET_CACHE[symbol] = {
                     "data": symbol_data,
                     "timestamp": current_time
                 }
            
        except Exception as e:
            print(f"Error fetching market status for {symbol}: {e}")
            # Try to use old cache even if expired if fetch failed
            if symbol in MARKET_CACHE:
                 data.append(MARKET_CACHE[symbol]["data"])
            else:
                # Add error placeholder
                data.append({
                    "symbol": symbol,
                    "name": symbol,
                    "price": 0.0,
                    "change": 0.0,
                    "percentChange": 0.0,
                    "history": []
                })
            
    return data

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
        
    def fluctuate(value):
        return round(value + random.uniform(-0.5, 0.5), 2)
    
    # Fetch real data for these symbols
    # For now, we'll use a mix of real data fetching (if we were fully implementing it) 
    # and the existing mock structure to keep it consistent with the rest of the app for now.
    # Ideally, we should do a batch fetch with yfinance.
    
    data = []
    try:
        # Batch fetch is better
        tickers = yf.Tickers(" ".join(symbols))
        
        for symbol in symbols:
            try:
                # Accessing tickers.tickers[symbol] might fail if symbol is invalid
                # But yfinance is a bit tricky with Tickers object, sometimes it's better to use Ticker individually for small lists
                # or use download() for batch.
                
                # Let's try individual for safety and simplicity in this context, 
                # though batch is better for performance.
                ticker = yf.Ticker(symbol)
                fast_info = ticker.fast_info
                
                price = fast_info.last_price
                prev_close = fast_info.previous_close
                
                if price and prev_close:
                    change = price - prev_close
                    percent_change = (change / prev_close) * 100
                    name = ticker.info.get('shortName', symbol)
                else:
                    # Fallback if data missing
                    price = 100.0
                    change = 0.0
                    percent_change = 0.0
                    name = symbol

                data.append({
                    "symbol": symbol,
                    "name": name,
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "percentChange": round(percent_change, 2)
                })
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                # Keep it in the list but with error data or skip? 
                # Let's show it with placeholder
                data.append({
                    "symbol": symbol,
                    "name": symbol,
                    "price": 0.0,
                    "change": 0.0,
                    "percentChange": 0.0
                })
                
    except Exception as e:
        print(f"Global error in watchlist fetch: {e}")
        return []

    return data


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
        # In a real app, we would fetch real data here to pass to the AI
        # For now, we'll simulate some market context or just ask for a general summary
        # based on "current" data (which the AI might not know if it's cut off, so we should provide context)
        
        # Let's construct a prompt with some of our mock data to make it realistic
        market_status = get_market_status()
        sectors = get_sectors()
        
        prompt = f"""
        Analyze the following market data and provide a comprehensive, 3-4 sentence summary of the day's stock market performance.
        
        Formatting Instructions:
        - Use **bold** for key terms, ticker symbols, and significant numbers.
        - Use [[green|text]] for positive trends, gains, or bullish signals.
        - Use [[red|text]] for negative trends, losses, or bearish signals.
        - Use [[blue|text]] for neutral observations or interesting highlights.

        Examples:
        - "The **S&P 500** saw a [[green|gain of 0.5%]] today."
        - "Tech stocks [[red|declined]] due to rate hike fears."
        
        Content Focus:
        - Start with the general market trend (indices).
        - Mention standout sectors (best and worst performers).
        - Conclude with a brief outlook or key takeaway.
        - Ensure the summary is 3-4 sentences long.
        
        Market Indices:
        {market_status}
        
        Sector Performance:
        {sectors}
        """
        
        if not client:
            return {"summary": "AI Summary is unavailable (Missing OpenAI API Key). Please set OPENAI_API_KEY environment variable."}

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful financial analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250
        )
        
        return {"summary": response.choices[0].message.content.strip()}
    except Exception as e:
        print(f"Error generating summary: {e}")
        # Fallback if OpenAI fails or key is missing
        return {"summary": "Market is showing mixed signals today with technology sector leading the charge while energy lags behind. Investors are cautiously optimistic ahead of upcoming economic data."}

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
