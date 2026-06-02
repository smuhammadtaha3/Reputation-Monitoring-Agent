from fastapi import FastAPI
from app.api.routes import router


app = FastAPI(
    title="AI Reputation Monitoring Agent",
    description="Monitors reviews, detects negatives, sends alerts, drafts responses.",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Reputation Agent is running"}
