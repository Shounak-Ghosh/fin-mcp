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

@app.get("/api/market-status")
def get_market_status():
    # Fetch data for major indices/futures
    tickers = ["ES=F", "NQ=F", "YM=F", "^VIX"]
    # data = yf.download(tickers, period="1d", interval="5m", progress=False)
    
    # Process data to return current price and change
    result = []
    # Note: yfinance structure can be complex with multiple tickers, simplified logic here for now
    # We might need to refine this based on actual yfinance output structure
    
    # Mocking structure for initial test to ensure endpoint works
    # In a real implementation we would parse the dataframe
    
    def fluctuate(value):
        return round(value + random.uniform(-0.5, 0.5), 2)

    return [
        {"symbol": "ES=F", "name": "S&P Futures", "price": fluctuate(6861.75), "change": fluctuate(-0.25), "percentChange": fluctuate(-0.003)},
        {"symbol": "NQ=F", "name": "NASDAQ Fut.", "price": fluctuate(25604.75), "change": fluctuate(-52.75), "percentChange": fluctuate(-0.21)},
        {"symbol": "YM=F", "name": "Dow Futures", "price": fluctuate(47898), "change": fluctuate(-56), "percentChange": fluctuate(-0.12)},
        {"symbol": "^VIX", "name": "VIX", "price": fluctuate(15.75), "change": fluctuate(-0.33), "percentChange": fluctuate(-2.05)},
    ]

@app.get("/api/watchlist")
def get_watchlist():
    # Mock data for now, will replace with real yfinance calls
    def fluctuate(value):
        return round(value + random.uniform(-0.5, 0.5), 2)
        
    return [
        {"symbol": "ORCL", "name": "Oracle Corporation", "price": fluctuate(214.38), "change": fluctuate(3.20), "percentChange": fluctuate(1.5)},
        {"symbol": "AVGO", "name": "Broadcom Inc.", "price": fluctuate(381.03), "change": fluctuate(0.11), "percentChange": fluctuate(0.03)},
        {"symbol": "AMZN", "name": "Amazon.com, Inc.", "price": fluctuate(229.11), "change": fluctuate(-1.41), "percentChange": fluctuate(-0.6)},
        {"symbol": "NVDA", "name": "NVIDIA Corporation", "price": fluctuate(183.46), "change": fluctuate(2.15), "percentChange": fluctuate(1.18)},
        {"symbol": "GOOG", "name": "Alphabet Inc.", "price": fluctuate(318.39), "change": fluctuate(-0.70), "percentChange": fluctuate(-0.22)},
    ]

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
        # Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
        history = ticker.history(period=period)
        
        if history.empty:
            return []
            
        # Format data for frontend
        data = []
        for date, row in history.iterrows():
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": round(row['Close'], 2)
            })
            
        return data
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
