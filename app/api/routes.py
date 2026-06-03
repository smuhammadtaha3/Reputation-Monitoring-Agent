from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.workers.tasks import poll_reviews
from app.core.database import supabase

router = APIRouter()

class IngestRequest(BaseModel):
    platform: str
    text: str
    stars: int
    author: str | None = None

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/ingest")
def ingest_review(req: IngestRequest):
    """Manually trigger processing of a single review. Great for testing."""
    from app.services.sentiment import analyze
    from app.services.scraper import has_competitor_mention
    from app.services.draft import generate_response
    from app.services.alert import send_alert
    from datetime import datetime

    sentiment = analyze(req.text)
    competitor = has_competitor_mention(req.text)
    should_alert = req.stars < 3 or sentiment["is_negative"] or competitor
    draft = None

    if should_alert:
        draft = generate_response(req.text, req.stars)
        review_dict = req.model_dump()
        review_dict["fetched_at"] = datetime.utcnow().isoformat()
        send_alert(review_dict, sentiment, draft)

    return {
        "sentiment": sentiment,
        "competitor_mentioned": competitor,
        "alert_sent": should_alert,
        "draft_response": draft
    }

@router.get("/reviews")
def get_reviews(limit: int = 20):
    """Returns recent reviews from Supabase."""
    result = (
        supabase.table("reviews")
        .select("*")
        .order("fetched_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data

@router.post("/trigger-poll")
def trigger_poll():
    """Manually fires the Celery poll task. Useful during dev."""
    task = poll_reviews.delay()
    return {"task_id": task.id, "status": "queued"}