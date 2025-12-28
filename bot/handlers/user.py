from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot import database, config

HELP_TEXT = f"""
Here are the available commands:
/start - Start the bot
/help - Show this help message
/about - Show info about the bot
/echo <text> - Echo back the text
/chatid - Get the current chat ID
/userid - Get your user ID
/stats - Bot usage & approval stats
/banned - View banned users list
/users - Get the total number of approved users in the database

Admin commands:
/approve <user_id> - Manually approve a user
/disapprove <user_id> - Remove user approval
/autoapprove <on/off> - Toggle auto-approval ON/OFF
/cooldown <seconds> - Set the approval cooldown
/limit <count> - Set the daily auto-approval limit
/blacklist <user_id> - Add a user to the blacklist
/unblacklist <user_id> - Remove a user from the blacklist
/logs - View approval & activity logs
/broadcast <message> - Send a message to all users
/ban <user_id> - Ban a user
/unban <user_id> - Unban a user

{config.FOOTER}
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message when the command /start is issued."""
    keyboard = [
        [
            InlineKeyboardButton("Main Channel", url=config.MAIN_CHANNEL),
            InlineKeyboardButton("Support Group", url=config.SUPPORT_LINK),
        ],
        [InlineKeyboardButton("Help & Commands", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    caption = f"Hi! I'm a bot that automatically approves new members.\n\n{config.FOOTER}"
    await update.message.reply_photo(
        photo=config.WELCOME_IMAGE,
        caption=caption,
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text(HELP_TEXT)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user's message."""
    await update.message.reply_text(update.message.text)


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns the chat id."""
    await update.message.reply_text(f"The chat id is: {update.effective_chat.id}")


async def user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns the user id."""
    await update.message.reply_text(f"Your user id is: {update.effective_user.id}")


async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bot usage & approval stats."""
    stats = database.stats.find_one()
    if stats:
        stats_message = "Bot Statistics:\n"
        for key, value in stats.items():
            if key != "_id":
                stats_message += f"{key.capitalize()}: {value}\n"
        await update.message.reply_text(stats_message)
    else:
        await update.message.reply_text("No statistics available yet.")


async def view_banned_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View banned users list."""
    banned_users = database.banned_users.find()
    banned_list = [str(user["user_id"]) for user in banned_users]
    if banned_list:
        await update.message.reply_text(f"Banned Users:\n" + "\n".join(banned_list))
    else:
        await update.message.reply_text("No users are currently banned.")


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info about the bot."""
    about_text = f"""
This is a Telegram bot that automatically approves new members in a chat.
It is managed by {config.OWNER_USERNAME}.

{config.FOOTER}
"""
    await update.message.reply_text(about_text)


async def total_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get the total number of approved users."""
    count = database.approved_users.count_documents({})
    await update.message.reply_text(f"Total approved users in the database: {count}")
