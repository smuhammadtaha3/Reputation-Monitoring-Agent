from app.core.database import supabase

def get_platform_stats() -> dict:
    result = supabase.table("reviews").select("*").execute()
    reviews = result.data
    if not reviews:
        return {}

    import pandas as pd
    df = pd.DataFrame(reviews)

    stats = {
        "total_reviews": len(df),
        "total_alerts": int(df["alert_sent"].sum()),
        "avg_star_rating": round(df["stars"].mean(), 2),
        "avg_sentiment_score": round(df["sentiment_score"].mean(), 4),
        "negative_count": int((df["sentiment_label"] == "negative").sum()),
        "positive_count": int((df["sentiment_label"] == "positive").sum()),
        "neutral_count": int((df["sentiment_label"] == "neutral").sum()),
        "competitor_mentions": int(df["competitor_mentioned"].sum()),
        "by_platform": df.groupby("platform").agg(
            total=("id", "count"),
            avg_stars=("stars", "mean"),
            negative=("alert_sent", "sum")
        ).round(2).to_dict("index")
    }
    return stats

def get_sentiment_trend() -> list:
    result = supabase.table("reviews")\
        .select("fetched_at, sentiment_label, sentiment_score, stars")\
        .order("fetched_at")\
        .execute()
    return result.data