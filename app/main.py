from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
app = FastAPI(
    title="AI Reputation Monitoring Agent",
    description="Monitors reviews, detects negatives, sends alerts, drafts responses.",
    version="2.0.0"
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
        "docs": "/docs",
        "health": "/api/v1/health"
    }
