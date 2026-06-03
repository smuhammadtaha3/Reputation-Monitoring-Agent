from datetime import datetime

COMPETITOR_KEYWORDS = [
    "mcdonald", "subway", "kfc", "burger king", "starbucks",
    "dominos", "pizza hut", "next door", "other place", "competitor"
]

def fetch_reviews(platform: str) -> list[dict]:
    """Mock reviews — replace with real API later"""
    return [
        {
            "platform": platform,
            "text": "Absolutely terrible service. Waited 45 minutes, staff was rude.",
            "stars": 1,
            "author": "Ahmed K.",
            "fetched_at": datetime.utcnow().isoformat()
        },
        {
            "platform": platform,
            "text": "Food was okay but honestly McDonald's nearby is way better.",
            "stars": 3,
            "author": "Sara M.",
            "fetched_at": datetime.utcnow().isoformat()
        },
        {
            "platform": platform,
            "text": "Lovely experience! Staff was helpful. Will definitely return.",
            "stars": 5,
            "author": "Ali R.",
            "fetched_at": datetime.utcnow().isoformat()
        },
        {
            "platform": platform,
            "text": "Never coming back. Worst experience of my life.",
            "stars": 1,
            "author": "John D.",
            "fetched_at": datetime.utcnow().isoformat()
        },
    ]

def has_competitor_mention(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in COMPETITOR_KEYWORDS)