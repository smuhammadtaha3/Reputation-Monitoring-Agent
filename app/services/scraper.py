from datetime import datetime

def fetch_reviews(platform: str) -> list[dict]:
    """
    Returns a list of review dicts.
    Replace each block with the real platform API call.
    """
    # --- MOCK DATA (replace with real API calls) ---
    mock_reviews = [
        {
            "platform": platform,
            "text": "Absolutely terrible service. Waited 45 minutes and no one helped.",
            "stars": 1,
            "author": "John D.",
            "fetched_at": datetime.utcnow().isoformat()
        },
        {
            "platform": platform,
            "text": "The food was okay but honestly McDonald's nearby is way better.",
            "stars": 3,
            "author": "Sara K.",
            "fetched_at": datetime.utcnow().isoformat()
        },
        {
            "platform": platform,
            "text": "Lovely experience! Will definitely come back.",
            "stars": 5,
            "author": "Ali R.",
            "fetched_at": datetime.utcnow().isoformat()
        },
    ]
    return mock_reviews

COMPETITOR_KEYWORDS = [
    "mcdonald", "subway", "kfc", "burger king", "starbucks",
    "competitor", "other place", "next door"
]

def has_competitor_mention(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in COMPETITOR_KEYWORDS)