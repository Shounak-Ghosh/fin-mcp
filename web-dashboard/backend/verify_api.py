import requests
import json

try:
    response = requests.get("http://localhost:8000/api/news")
    if response.status_code == 200:
        news = response.json()
        print(f"Successfully fetched {len(news)} articles.")
        if news:
            print("First article:")
            print(json.dumps(news[0], indent=2))
    else:
        print(f"Failed to fetch news. Status code: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error connecting to API: {e}")
