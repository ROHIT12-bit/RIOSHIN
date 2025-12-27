import os

ADMIN_USER_IDS = [int(i) for i in os.getenv("ADMIN_USER_IDS", "").split(",") if i]
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
