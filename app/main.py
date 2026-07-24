from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.api.routes import router
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def run_poll():
    """Ye function har 15 minute mein chalta hai"""
    try:
        logger.info("Auto-poll starting...")
        from app.workers.tasks import poll_reviews
        result = poll_reviews()
        logger.info(f"Auto-poll done: {result}")
    except Exception as e:
        logger.error(f"Auto-poll error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — model preload karo taake pehli request timeout na ho
    logger.info("Preloading sentiment model...")
    logger.info("Model loaded successfully")

    # Scheduler shuru karo
    scheduler.add_job(
        run_poll,
        'interval',
        minutes=15,
        id='review_poller',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started — polling every 15 minutes")
    yield
    # Shutdown — scheduler band karo
    scheduler.shutdown()
    logger.info("Scheduler stopped")

app = FastAPI(
    title="AI Reputation Monitoring Agent",
    description="Monitors reviews, detects negatives, sends alerts, drafts responses.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/dashboard")
def dashboard():
    return FileResponse("frontend/index.html")

@app.get("/")
def root():
    return {
        "message": "AI Reputation Monitoring Agent",
        "version": "2.0.0",
        "scheduler": "running" if scheduler.running else "stopped",
        "next_poll": str(scheduler.get_job('review_poller').next_run_time)
                     if scheduler.get_job('review_poller') else "not scheduled",
        "docs": "/docs"
    }