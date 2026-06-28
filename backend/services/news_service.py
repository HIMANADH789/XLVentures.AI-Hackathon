import os
import requests
import time
from datetime import datetime, timedelta
from config import settings
from utils.retry import with_retries

@with_retries(max_retries=3, initial_delay=1.0)
def search_news(company_name: str) -> list:
    """Search NewsAPI for recent news about a company name over the last 90 days."""
    api_key = settings.news_api_key or os.getenv("NEWS_API_KEY")
    if not api_key:
        print("[NEWSAPI] No API key configured. Skipping news search.")
        return []
        
    print(f"[NEWSAPI] News search started for query: {company_name}")
    start_time = time.time()
    try:
        from_date = (datetime.now() - timedelta(days=28)).strftime('%Y-%m-%d')
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": company_name,
            "from": from_date,
            "sortBy": "relevancy",
            "language": "en",
            "pageSize": 10,
            "apiKey": api_key
        }
        response = requests.get(url, params=params, timeout=10)
        duration = time.time() - start_time
        print(f"[NEWSAPI] News search completed in {duration:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            results = []
            for art in articles:
                if art.get("title") and art.get("title") != "[Removed]":
                    results.append({
                        "title": art.get("title"),
                        "description": art.get("description"),
                        "url": art.get("url"),
                        "publishedAt": art.get("publishedAt")
                    })
            return results
        else:
            print(f"[NEWSAPI ERROR] Response code {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[NEWSAPI ERROR] Failed to fetch news for {company_name}: {e}")
        
    return []
