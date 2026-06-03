"""
Telegram Bot Service for sending alerts and notifications
"""
import logging
from telegram import Bot
from telegram.error import TelegramError
from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    """Service for managing Telegram bot communications"""
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        if not self.bot_token:
            logger.warning("Telegram bot token not configured")
            self.bot = None
        else:
            self.bot = Bot(token=self.bot_token)
    
    async def send_alert(self, message: str, chat_id: int = None) -> bool:
        """
        Send an alert message via Telegram
        
        Args:
            message: The alert message to send
            chat_id: Telegram chat ID (optional, uses default if not provided)
        
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            if chat_id:
                await self.bot.send_message(chat_id=chat_id, text=message, parse_mode="HTML")
            else:
                logger.warning("No chat ID provided for sending alert")
                return False
            
            logger.info(f"Alert sent to chat {chat_id}")
            return True
        
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram alert: {str(e)}")
            return False
    
    async def send_negative_review_alert(self, review_data: dict) -> bool:
        """
        Send formatted alert for negative reviews
        
        Args:
            review_data: Dictionary containing review information
            - content: Review text
            - rating: Review rating
            - source: Where the review came from
            - sentiment: Sentiment analysis result
        
        Returns:
            bool: True if sent successfully
        """
        try:
            message = f"""
🚨 <b>Negative Review Alert</b>

📝 <b>Content:</b>
{review_data.get('content', 'N/A')}

⭐ <b>Rating:</b> {review_data.get('rating', 'N/A')}
🔗 <b>Source:</b> {review_data.get('source', 'N/A')}
😠 <b>Sentiment:</b> {review_data.get('sentiment', 'N/A')}
"""
            chat_id = settings.telegram_chat_id
            return await self.send_alert(message, chat_id)
        
        except Exception as e:
            logger.error(f"Error formatting negative review alert: {str(e)}")
            return False
    
    async def send_draft_response(self, review_id: str, draft_response: str) -> bool:
        """
        Send draft response for review
        
        Args:
            review_id: ID of the review
            draft_response: The drafted response
        
        Returns:
            bool: True if sent successfully
        """
        try:
            message = f"""
✍️ <b>Draft Response Ready</b>

📌 <b>Review ID:</b> {review_id}

💬 <b>Your Response:</b>
{draft_response}

Please review and customize before posting.
"""
            chat_id = settings.telegram_chat_id
            return await self.send_alert(message, chat_id)
        
        except Exception as e:
            logger.error(f"Error sending draft response: {str(e)}")
            return False


# Create singleton instance
telegram_service = TelegramBotService()
