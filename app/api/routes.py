from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.core.database import supabase
from app.services.analytics import get_platform_stats, get_sentiment_trend

router = APIRouter()

class IngestRequest(BaseModel):
    platform: str
    text: str
    stars: int
    author: str | None = None

@router.get("/health")
def health():
    return {"status": "ok", "message": "Reputation Agent is running"}

@router.post("/ingest")
def ingest_review(req: IngestRequest):
    from app.services.sentiment import analyze
    from app.services.scraper import has_competitor_mention
    from app.services.draft import generate_response
    from app.services.alert import send_alert

    sentiment = analyze(req.text)
    competitor = has_competitor_mention(req.text)
    should_alert = (
        req.stars < 3 or
        sentiment["is_negative"] or
        competitor
    )
    draft = None

    if should_alert:
        draft = generate_response(req.text, req.stars)
        review_dict = req.model_dump()
        review_dict["fetched_at"] = datetime.utcnow().isoformat()
        send_alert(review_dict, sentiment, draft)

    supabase.table("reviews").insert({
        "platform": req.platform,
        "text": req.text,
        "stars": req.stars,
        "author": req.author,
        "sentiment_label": sentiment["label"],
        "sentiment_score": sentiment["score"],
        "competitor_mentioned": competitor,
        "alert_sent": should_alert,
        "draft_response": draft,
        "fetched_at": datetime.utcnow().isoformat()
    }).execute()

    return {
        "sentiment": sentiment,
        "competitor_mentioned": competitor,
        "alert_sent": should_alert,
        "draft_response": draft
    }

@router.get("/reviews")
def get_reviews(limit: int = 20):
    result = supabase.table("reviews")\
        .select("*")\
        .order("fetched_at", desc=True)\
        .limit(limit)\
        .execute()
    return result.data

@router.get("/analytics")
def analytics():
    return get_platform_stats()

@router.get("/analytics/trend")
def trend():
    return get_sentiment_trend()

@router.post("/trigger-poll")
def trigger_poll():
    from app.workers.tasks import poll_reviews
    result = poll_reviews()
    return {"status": "completed", "result": result}

@router.get("/scheduler/status")
def scheduler_status():
    """Scheduler ka status aur next run time"""
    from app.main import scheduler
    job = scheduler.get_job('review_poller')
    return {
        "running": scheduler.running,
        "next_poll": str(job.next_run_time) if job else None,
        "job_id": "review_poller"
    }