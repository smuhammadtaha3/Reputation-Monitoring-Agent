import asyncio
import telegram
from app.core.config import settings

async def _send(message: str):
    bot = telegram.Bot(token=settings.telegram_bot_token)
    async with bot:
        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=message,
            parse_mode="Markdown"
        )

def send_alert(review: dict, sentiment: dict, draft: str):
    stars = "⭐" * max(1, review.get("stars", 1))
    message = (
        f"🚨 *New Alert — {review['platform'].title()}*\n"
        f"Rating: {stars}\n"
        f"Sentiment: `{sentiment['label']}` ({sentiment['score']})\n\n"
        f"*Review:*\n_{review['text'][:200]}_\n\n"
        f"*Suggested Reply:*\n{draft}"
    )
    asyncio.run(_send(message))