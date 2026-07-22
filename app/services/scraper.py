import json, os, random
from datetime import datetime

COMPETITOR_KEYWORDS = ["mcdonald", "subway", "kfc", "burger king", "starbucks", "dominos", "pizza hut"]

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/yelp_80000_fixed.json")
_pool = None
_used = set()

def _load_pool():
    global _pool
    if _pool is None:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _pool = json.load(f)
    return _pool

def fetch_reviews(platform: str, batch_size: int = 4) -> list[dict]:
    """Simulates live ingestion by rotating through a real review dataset."""
    pool = _load_pool()
    available = [i for i in range(len(pool)) if i not in _used]
    if len(available) < batch_size:
        _used.clear()
        available = list(range(len(pool)))

    picks = random.sample(available, min(batch_size, len(available)))
    _used.update(picks)

    results = []
    for i in picks:
        r = pool[i]
        results.append({
            "platform": platform,
            "text": r["text"],
            "stars": r["stars"],
            "author": f"User{i}",
            "fetched_at": datetime.utcnow().isoformat()
        })
    return results

def has_competitor_mention(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in COMPETITOR_KEYWORDS)