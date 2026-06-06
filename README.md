# AI Reputation Monitoring Agent

I'm Still working on this project
project live at: https://reputation-monitoring-agent-production.up.railway.app/dashboard

## 📚 Project Overview
The **AI Reputation Monitoring Agent** is a production‑ready system that continuously monitors online review platforms, classifies sentiment with a pre‑trained RoBERTa model, generates response drafts via Groq‑hosted LLaMA 3.3 70B, stores everything in Supabase (PostgreSQL), and pushes real‑time alerts to a Telegram channel. The platform is fully containerised and deployed on Railway.

---

## 🏗️ Architecture
```text
+-------------------+      +-------------------+      +-------------------+
|   Review Sources  | ---> |   FastAPI Backend | ---> |   AI Engine       |
| (Google, FB, …)  |      |   (Railway)       |      | (HuggingFace RoBERTa,
|                   |      | - Sentiment       |      |  Groq LLaMA)      |
+-------------------+      +-------------------+      +-------------------+
                                   |                     |
                                   v                     v
                            +-------------------+   +-------------------+
                            |   Data Layer      |   | Scheduler & Queue |
                            | (Supabase / PG)   |   | (Celery + Redis) |
                            | - Reviews, Alerts|   +-------------------+
                            +-------------------+            |
                                   |                       |
                                   v                       v
                            +---------------------------------------+
                            |   Notification Service (Telegram Bot) |
                            +---------------------------------------+
```

---

## ⚙️ Tech Stack
| Layer | Technologies |
|------|----------------|
| **API** | FastAPI, Uvicorn, Pydantic |
| **NLP** | HuggingFace Transformers, `cardiffnlp/twitter-roberta-base-sentiment` (PyTorch) |
| **AI/ML Models & Libraries** | Pandas,Matplotlib, Scikit-Learn, Seaborn, WrodNetLemmatizer, Stopwrods, Logistic Regression,Naive Bayes,   |
| **Generative AI** | Groq API → LLaMA 3.3 70B |
| **Data** | Supabase (PostgreSQL), SQLAlchemy |
| **Queue** | Celery, Redis (Upstash) |
| **Alerts** | python‑telegram‑bot |
| **Deployment** | Railway, Docker |
| **Future UI** | React, Recharts |

---

## 📦 Installation & Quick‑Start
```bash
# Clone the repo
git clone https://github.com/smuhammadtaha3/Reputation-Monitoring-Agent.git
cd Reputation-Monitoring-Agent

# Virtual environment
python -m venv .venv && ./.venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (Railway UI or .env file)
# --------------------------------------------------
# GROQ_API_KEY          – Groq authentication token
# SUPABASE_URL          – Supabase project URL
# SUPABASE_KEY          – Supabase service key
# TELEGRAM_BOT_TOKEN    – Bot token from BotFather
# TELEGRAM_CHAT_ID      – Chat ID where alerts are sent
# --------------------------------------------------

# Run the API server
uvicorn app.main:app --reload

# In another terminal, start the worker & beat
celery -A app.workers.celery_app worker -B
```

---

## 🔀 API Endpoints (`/api/v1`)
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check – returns `{status: "ok"}` |
| `POST` | `/ingest` | Accepts a review payload, runs sentiment analysis, optional competitor detection, generates a draft, stores the record, and sends a Telegram alert if needed |
| `GET` | `/reviews?limit=20` | Returns the most recent **limit** reviews from Supabase |
| `GET` | `/analytics` | Summary statistics (total reviews, avg rating, sentiment breakdown, etc.) |
| `GET` | `/analytics/trend` | Raw time‑series data for building sentiment trend charts |
| `POST` | `/trigger-poll` | Manually trigger the Celery task that polls external platforms (used for Phase 2) |
| `GET` | `/` | Simple JSON with service metadata |
| `GET` | `/dashboard` | Serves the React UI once Phase 4 is completed |

---

## 📂 Service Modules (high‑level description)
### `app/services/sentiment.py`
```python
from transformers import pipeline
sentiment_pipe = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

def analyze(text: str) -> dict:
    result = sentiment_pipe(text[:512])[0]
    label = result["label"].lower()
    score = round(result["score"], 4)
    return {"label": label, "score": score, "is_negative": label == "negative"}
```
*Performs tokenisation, runs RoBERTa inference, returns label + confidence.*

### `app/services/draft.py`
```python
import httpx

def generate_response(review: str, stars: int) -> str:
    prompt = (
        f"You are a professional support agent. Write a courteous reply to the following review.\n"
        f"Review ({stars}★): {review}\n"
        "Reply:" 
    )
    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.groq_api_key}"},
        json={"model": "llama-3.3-70b", "messages": [{"role": "user", "content": prompt}], "max_tokens": 250},
    )
    return resp.json()["choices"][0]["message"]["content"].strip()
```
*Uses Groq LLaMA 3.3 70B to produce a brand‑aligned reply.*

### `app/services/scraper.py`
```python
COMPETITOR_KEYWORDS = {"mcdonald", "subway", "kfc", "burger king"}

def has_competitor_mention(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in COMPETITOR_KEYWORDS)
```
*Simple rule‑based detection for competitor mentions.*

### `app/services/alert.py`
Sends a formatted Telegram message containing the platform, rating, sentiment, raw review (truncated), and the AI‑generated draft.

### `app/services/analytics.py`
Provides two helper functions:
- `get_platform_stats()` – aggregates counts, averages, and per‑platform breakdown using **pandas**.
- `get_sentiment_trend()` – returns chronological raw data for charting.

---

## 🗄️ Database Schema (Supabase / PostgreSQL)
```sql
CREATE TABLE reviews (
    id                BIGSERIAL PRIMARY KEY,
    platform          TEXT NOT NULL,
    text              TEXT NOT NULL,
    stars             INT NOT NULL,
    author            TEXT,
    sentiment_label   TEXT,
    sentiment_score   NUMERIC,
    competitor_mentioned BOOLEAN,
    alert_sent        BOOLEAN,
    draft_response    TEXT,
    fetched_at        TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```
*All fields are inserted by the `/ingest` endpoint.*

---

## 🕒 Background Workers (Celery)
- **`celery_app.py`** – creates the Celery instance with Redis broker.
- **`tasks.py`** – defines `poll_reviews` (Phase 2) that will fetch real data from Google/Yelp APIs and push them through the same pipeline.
- **Beat schedule** – runs every 15 minutes (`celery -B`).

---

## 📣 Telegram Bot Integration
The bot uses **asyncio** to send markdown‑formatted alerts. Environment variables:
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=123456789
```
Message example:
```
🚨 *New Alert — Google Reviews*
Rating: ⭐⭐⭐
Sentiment: `negative` (0.97)

*Review:*
_The food was cold and the service rude..._

*Suggested Reply:*
We’re sorry to hear about your experience. …
```

---

## 📈 Future Roadmap
| Phase | Goal |
|------|------|
| **2** | Integrate **Google Places API** and **Yelp Fusion API** to fetch real reviews automatically. |
| **3** | Build analytical dashboards with **Pandas** and expose CSV/JSON exports. |
| **4** | Develop a **React** frontend (`frontend/`) showing live review feed, alert history, and trend charts (Recharts/Chart.js). |
| **5** | Fine‑tune the RoBERTa model on domain‑specific review data; add custom competitor detection with NER; implement sentiment trend prediction using time‑series models. |

---

## 🛠️ Development & Testing
1. Run the API & worker locally as described above.
2. Use **`curl`** or **Postman** to POST to `/api/v1/ingest`:
```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"platform":"google","text":"The product broke after one day.","stars":1,"author":"John Doe"}'
```
3. Verify the alert appears in the configured Telegram chat and the record shows up in Supabase.
4. Run unit tests (if any) with `pytest`.

---

## 📜 License
MIT – feel free to fork, extend, or commercialise.

---

### 🎉 Enjoy!
You now have a complete, production‑grade README that documents **every moving part** of the AI Reputation Monitoring Agent. Use it as a reference for onboarding new engineers, for CI/CD pipelines, or to hand‑off the project to another AI assistant.
