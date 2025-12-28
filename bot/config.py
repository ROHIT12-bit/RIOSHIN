import os

ADMIN_USER_IDS = [int(i) for i in os.getenv("ADMIN_USER_IDS", "").split(",") if i]
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
START_IMAGE_URL = os.getenv("START_IMAGE_URL", "https://te.legra.ph/file/11b3334823b8f5d02e6e3.jpg")
