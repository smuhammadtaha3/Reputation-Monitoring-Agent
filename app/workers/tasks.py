from app.services.scraper import fetch_reviews, has_competitor_mention
from app.services.sentiment import analyze
from app.services.draft import generate_response
from app.services.alert import send_alert
from app.core.database import supabase
from datetime import datetime

PLATFORMS = ["google", "yelp", "facebook", "trustpilot", "linkedin"]


def poll_reviews():
    results = {"processed": 0, "alerts_sent": 0, "platforms": []}

    for platform in PLATFORMS:
        reviews = fetch_reviews(platform)
        platform_alerts = 0

        for review in reviews:
            sentiment = analyze(review["text"])
            competitor = has_competitor_mention(review["text"])
            should_alert = (
                review["stars"] < 3 or
                sentiment["is_negative"] or
                competitor
            )
            draft = None

            if should_alert:
                draft = generate_response(review["text"], review["stars"])
                send_alert(review, sentiment, draft)
                platform_alerts += 1

            supabase.table("reviews").insert({
                "platform": platform,
                "text": review["text"],
                "stars": review["stars"],
                "author": review.get("author"),
                "sentiment_label": sentiment["label"],
                "sentiment_score": sentiment["score"],
                "competitor_mentioned": competitor,
                "alert_sent": should_alert,
                "draft_response": draft,
                "fetched_at": review["fetched_at"]
            }).execute()

            results["processed"] += 1

        results["alerts_sent"] += platform_alerts
        results["platforms"].append({
            "name": platform,
            "reviews": len(reviews),
            "alerts": platform_alerts
        })

    return results