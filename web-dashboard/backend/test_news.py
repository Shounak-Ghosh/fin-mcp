import yfinance as yf
import json

def check_news():
    tickers = ["NVDA", "^GSPC"]
    for symbol in tickers:
        print(f"--- News for {symbol} ---")
        ticker = yf.Ticker(symbol)
        news = ticker.news
        if news:
            print(json.dumps(news[0], indent=2))
        else:
            print("No news found")

if __name__ == "__main__":
    check_news()
