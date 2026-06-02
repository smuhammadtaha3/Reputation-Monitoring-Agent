from app.workers.celery_app import celery
from app.services.scraper import fetch_reviews, has_competitor_mention
from app.services.sentiment import analyze
from app.services.draft import generate_response
from app.services.alert import send_alert
from app.core.database import supabase

PLATFORMS = ["google", "yelp", "facebook", "trustpilot", "linkedin"]
ALERT_THRESHOLD_STARS = 3

@celery.task(name="app.workers.tasks.poll_reviews")
def poll_reviews():
    """Runs every 15 minutes. Fetches, analyzes, alerts, stores."""
    for platform in PLATFORMS:
        reviews = fetch_reviews(platform)

        for review in reviews:
            sentiment = analyze(review["text"])
            competitor = has_competitor_mention(review["text"])

            # Decide if this review needs an alert
            should_alert = (
                review["stars"] < ALERT_THRESHOLD_STARS or
                sentiment["is_negative"] or
                competitor
            )

            draft = None
            if should_alert:
                draft = generate_response(review["text"], review["stars"])
                send_alert(review, sentiment, draft)

            # Store everything in Supabase
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

    return {"status": "done", "platforms_checked": len(PLATFORMS)}