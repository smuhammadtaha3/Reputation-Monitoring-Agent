from groq import Groq
from app.core.config import settings

_client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = (
    "You are a professional business reputation manager. "
    "Write concise, empathetic, professional responses to customer reviews. "
    "Keep replies under 80 words. Never be defensive."
)

def generate_response(review_text: str, star_rating: int) -> str:
    chat = _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"Customer left a {star_rating}-star review:\n\n"
                f'"{review_text}"\n\nWrite a professional response.'
            )}
        ],
        max_tokens=150
    )
    return chat.choices[0].message.content.strip()