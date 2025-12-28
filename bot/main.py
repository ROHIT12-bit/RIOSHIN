import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatJoinRequestHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from bot import config, database
from bot.handlers import admin, user
from bot.logging import log_message

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcomes new members to the chat and approves them."""
    settings = database.settings.find_one()
    if not settings or not settings.get("auto_approve_enabled", True):
        return

    new_member = update.effective_user
    if not new_member:
        return

    # Check if user is banned or blacklisted
    if database.banned_users.find_one({"user_id": new_member.id}) or \
       database.blacklist.find_one({"user_id": new_member.id}):
        logger.info(f"User {new_member.id} is banned or blacklisted, declining join request.")
        await update.chat_join_request.decline()
        await log_message("auto_decline_banned", user_id=new_member.id, context=context)
        return

    # Force sub
    if config.FORCE_SUB_CHANNEL:
        try:
            member = await context.bot.get_chat_member(config.FORCE_SUB_CHANNEL, update.effective_user.id)
            if member.status not in ["member", "administrator", "creator"]:
                await context.bot.send_message(
                    update.effective_chat.id,
                    f"You must join our channel to be approved. Please join {config.FORCE_SUB_CHANNEL} and then request to join again."
                )
                return
        except Exception as e:
            logger.error(f"Error checking chat member status: {e}")
            return

    # Check cooldown
    cooldown_period = settings.get("cooldown_period", 0)
    last_approval = database.logs.find_one({"action": "auto_approve"}, sort=[("timestamp", -1)])
    if last_approval and last_approval.get("timestamp") and last_approval["timestamp"] + timedelta(seconds=cooldown_period) > datetime.now():
        return

    # Check daily limit
    daily_limit = settings.get("daily_approval_limit", 0)
    if daily_limit > 0:
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        approvals_today = database.logs.count_documents({
            "action": "auto_approve",
            "timestamp": {"$gte": start_of_day, "$lt": end_of_day}
        })
        if approvals_today >= daily_limit:
            return

    chat_id = update.effective_chat.id

    await update.chat_join_request.approve()
    database.approved_users.insert_one({"user_id": new_member.id})
    database.stats.update_one({}, {"$inc": {"approved": 1}}, upsert=True)
    await log_message("auto_approve", user_id=new_member.id, context=context)
    await context.bot.send_message(
        chat_id, f"Welcome {new_member.mention_html()}! Your join request has been approved."
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles unknown commands."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    if query.data == "help":
        await query.edit_message_text(text=user.help_command.help_text)
    elif query.data == "commands":
        await query.edit_message_text(text=user.help_command.help_text)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    # User commands
    application.add_handler(CommandHandler("start", user.start))
    application.add_handler(CommandHandler("help", user.help_command))
    application.add_handler(CommandHandler("about", user.about))
    application.add_handler(CommandHandler("echo", user.echo))
    application.add_handler(CommandHandler("chatid", user.chat_id))
    application.add_handler(CommandHandler("userid", user.user_id))
    application.add_handler(CommandHandler("approved", user.approved_users_count))
    application.add_handler(CommandHandler("stats", user.bot_stats))
    application.add_handler(CommandHandler("banned", user.view_banned_users))
    application.add_handler(CommandHandler("users", user.total_users))

    # Admin commands
    application.add_handler(CommandHandler("approve", admin.approve))
    application.add_handler(CommandHandler("disapprove", admin.disapprove))
    application.add_handler(CommandHandler("autoapprove", admin.auto_approve_toggle))
    application.add_handler(CommandHandler("cooldown", admin.set_cooldown))
    application.add_handler(CommandHandler("limit", admin.set_limit))
    application.add_handler(CommandHandler("blacklist", admin.blacklist_user))
    application.add_handler(CommandHandler("unblacklist", admin.unblacklist_user))
    application.add_handler(CommandHandler("logs", admin.view_logs))
    application.add_handler(CommandHandler("broadcast", admin.broadcast))
    application.add_handler(CommandHandler("ban", admin.ban))
    application.add_handler(CommandHandler("unban", admin.unban))

    # Other handlers
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(ChatJoinRequestHandler(auto_approve))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
