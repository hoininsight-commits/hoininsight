# src/agents/collectors/social_prediction_collector.py

import requests
import json
import math
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

class SocialPredictionCollector:
    """
    [RESTORED] Polymarket and Hacker News intelligence collector.
    Adapted from last30days-skill for HOIN Insight v10.2.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": "HOIN-Insight-Intelligence-Bot/10.2 (Autonomous Discovery)"
        }
        self.gamma_api_url = "https://gamma-api.polymarket.com/public-search"
        self.hn_api_url = "https://hn.algolia.com/api/v1/search"

    def collect_polymarket(self, query: str) -> list:
        """Collect active prediction markets from Polymarket."""
        try:
            params = {
                "q": query,
                "page": "1",
                "events_status": "active",
                "keep_closed_markets": "0"
            }
            resp = requests.get(self.gamma_api_url, params=params, headers=self.headers, timeout=10)
            if resp.status_code != 200:
                return []
            
            data = resp.json()
            events = data.get("events", [])
            results = []
            
            for ev in events:
                # Basic relevance check
                title = ev.get("title", "")
                if query.lower() not in title.lower():
                    continue
                
                markets = ev.get("markets", [])
                if not markets: continue
                
                # Get the most liquid market
                top_market = sorted(markets, key=lambda x: float(x.get("liquidity", 0) or 0), reverse=True)[0]
                
                # Parse outcomes
                outcomes = []
                try:
                    outcome_names = json.loads(top_market.get("outcomes", "[]"))
                    prices = json.loads(top_market.get("outcomePrices", "[]"))
                    for name, price in zip(outcome_names, prices):
                        outcomes.append({"name": name, "probability": round(float(price) * 100, 1)})
                except:
                    pass

                results.append({
                    "title": title,
                    "url": f"https://polymarket.com/event/{ev.get('slug')}",
                    "outcomes": outcomes,
                    "liquidity": float(top_market.get("liquidity", 0) or 0),
                    "volume24h": float(top_market.get("volume24hr", 0) or 0)
                })
            
            return sorted(results, key=lambda x: x["liquidity"], reverse=True)[:5]
        except Exception as e:
            print(f"  ⚠️ Polymarket collection error ({query}): {e}")
            return []

    def collect_hacker_news(self, query: str) -> list:
        """Collect top stories and discussions from Hacker News."""
        try:
            # Last 7 days unix timestamp
            since_ts = int((datetime.now() - timedelta(days=7)).timestamp())
            params = {
                "query": query,
                "tags": "story",
                "numericFilters": f"created_at_i>{since_ts},points>5",
                "hitsPerPage": "10"
            }
            resp = requests.get(self.hn_api_url, params=params, headers=self.headers, timeout=10)
            if resp.status_code != 200:
                return []
            
            hits = resp.json().get("hits", [])
            results = []
            for hit in hits:
                results.append({
                    "title": hit.get("title"),
                    "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    "points": hit.get("points"),
                    "comments": hit.get("num_comments"),
                    "author": hit.get("author"),
                    "date": hit.get("created_at")[:10]
                })
            return results
        except Exception as e:
            print(f"  ⚠️ Hacker News collection error ({query}): {e}")
            return []

    def collect_all(self, keywords: list) -> dict:
        """Run collection across all sources for given keywords."""
        all_pm = []
        all_hn = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            pm_futures = [executor.submit(self.collect_polymarket, kw) for kw in keywords]
            hn_futures = [executor.submit(self.collect_hacker_news, kw) for kw in keywords]
            
            for f in as_completed(pm_futures):
                all_pm.extend(f.result())
            for f in as_completed(hn_futures):
                all_hn.extend(f.result())
        
        # Dedup and sort
        dedup_pm = {item['url']: item for item in all_pm}.values()
        dedup_hn = {item['url']: item for item in all_hn}.values()
        
        return {
            "polymarket": sorted(list(dedup_pm), key=lambda x: x['liquidity'], reverse=True),
            "hacker_news": sorted(list(dedup_hn), key=lambda x: x['points'], reverse=True)
        }

if __name__ == "__main__":
    collector = SocialPredictionCollector()
    test_keywords = ["Nvidia", "Interest Rates", "AI"]
    print(f"🔍 Testing SocialPredictionCollector with {test_keywords}...")
    results = collector.collect_all(test_keywords)
    print(f"✅ Found {len(results['polymarket'])} Polymarket events")
    print(f"✅ Found {len(results['hacker_news'])} HN stories")
    print(json.dumps(results, indent=2, ensure_ascii=False))
