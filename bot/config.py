# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐑𝐎𝐇𝐈𝐓 | 𝐁𝐎𝐓𝐒𝐊𝐈𝐍𝐆𝐃𝐎𝐌𝐒
# 𝐓𝐆 𝐈𝐃 : @𝐁𝐎𝐓𝐒𝐊𝐈𝐍𝐆𝐃𝐎𝐌𝐒
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐒 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
import os

# ---------- SENSITIVE CONFIGS ----------
# These must be set as environment variables for security.
# DO NOT HARDCODE THESE VALUES IN THIS FILE.
BOT_TOKEN   = os.getenv("BOT_TOKEN")
API_ID      = os.getenv("API_ID")
API_HASH    = os.getenv("API_HASH")
MONGO_URI   = os.getenv("MONGO_URI")

# This is used to identify who can use the admin commands.
# It must be a comma-separated list of integer user IDs.
ADMIN_USER_IDS = [int(i) for i in os.getenv("ADMIN_USER_IDS", "").split(",") if i]


# ---------- EDITABLE CONFIGS ----------
# These can be edited directly here, or overridden by environment variables.
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@BOTSKINGDOMS")

# --- Bot Behavior ---
# A comma-separated list of channel usernames (without '@') that users must join.
# Example: "channel1,channel2,channel3"
# The bot will check up to the first 5 channels listed.
# Leave blank to disable the "force subscribe" feature.
FORCE_SUB_CHANNELS = [
    channel.strip()
    for channel in os.getenv("FORCE_SUB_CHANNELS", "BOTSKINGDOMS").split(",")
    if channel.strip()
][:5]  # Limit to a maximum of 5 channels

AUTO_APPROVE_INSTANT = os.getenv("AUTO_APPROVE_INSTANT", "True").lower() == "true"
SEND_WELCOME_IN_CHAT = os.getenv("SEND_WELCOME_IN_CHAT", "True").lower() == "true"

# --- Customization ---
WELCOME_IMAGE = os.getenv("WELCOME_IMAGE", "https://i.ibb.co/bMFcCB6B/59kLh.jpg")
FOOTER = os.getenv("FOOTER", "Powered by @BOTSKINGDOMS ⚡")

# --- Links ---
# These are used for the buttons in the /start message.
MAIN_CHANNEL = os.getenv("MAIN_CHANNEL", "https://t.me/BOTSKINGDOMS")
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/BOTSKINGDOMSGROUP")

# --- Logging ---
# The chat ID of the channel where the bot should send logs.
# Set to 0 to disable sending logs to a channel.
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "0"))
