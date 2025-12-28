from datetime import datetime
from telegram.ext import ContextTypes
from bot import config, database

async def log_message(action: str, user_id: int = None, details: str = "", context: ContextTypes.DEFAULT_TYPE = None):
    """Send a message to the log channel and save it to the database."""
    log_entry = {
        "action": action,
        "user_id": user_id,
        "details": details,
        "timestamp": datetime.now()
    }
    database.logs.insert_one(log_entry)

    if config.LOG_CHAT_ID and config.LOG_CHAT_ID != 0 and context:
        message = f"#{action}\n"
        if user_id:
            message += f"User ID: `{user_id}`\n"
        if details:
            message += f"Details: {details}\n"

        try:
            await context.bot.send_message(chat_id=config.LOG_CHAT_ID, text=message)
        except Exception as e:
            # Avoid logging this error to prevent a potential loop
            print(f"Failed to send log message to channel {config.LOG_CHAT_ID}: {e}")
