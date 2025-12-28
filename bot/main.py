import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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


async def get_user_join_status(
    channel: str, user_id: int, context: ContextTypes.DEFAULT_TYPE
) -> tuple[str, bool]:
    """Checks if a user has joined a specific channel."""
    try:
        member = await context.bot.get_chat_member(f"@{channel}", user_id)
        return channel, member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Error checking status for @{channel}: {e}")
        # Fail open: If the check fails, assume the user has joined to avoid blocking.
        return channel, True


async def handle_force_sub(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
) -> None:
    """
    Sends a message to the user with a list of channels to join and a button
    to confirm they have joined.
    """
    # Check membership status for all force-sub channels concurrently
    tasks = [
        get_user_join_status(channel, user_id, context)
        for channel in config.FORCE_SUB_CHANNELS
    ]
    results = await asyncio.gather(*tasks)

    unjoined_channels = [channel for channel, joined in results if not joined]

    if not unjoined_channels:
        # If all channels are joined, finalize the approval
        await finalize_approval(update, context)
        return

    # Build the UI with channel links and status indicators
    keyboard = []
    for channel, joined in results:
        status_icon = "✅" if joined else "❌"
        status_text = f"{status_icon} Joined" if joined else f"{status_icon} Not Joined"
        row = [InlineKeyboardButton(status_text, callback_data=f"status_{channel}")]

        if not joined:
            row.append(
                InlineKeyboardButton(
                    f"Join '{channel}'", url=f"https://t.me/{channel}"
                )
            )
        keyboard.append(row)

    # Add the final confirmation button
    keyboard.append(
        [
            InlineKeyboardButton(
                "✅ I have joined", callback_data="check_join_status"
            )
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        user_id,
        "You must join our channel(s) to be approved. Please join the channels below and then click the button.",
        reply_markup=reply_markup,
    )


async def check_join_status_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handles the '✅ I have joined' button press. Re-checks channel memberships
    and either approves the user or updates the message.
    """
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    tasks = [
        get_user_join_status(channel, user_id, context)
        for channel in config.FORCE_SUB_CHANNELS
    ]
    results = await asyncio.gather(*tasks)
    all_joined = all(joined for _, joined in results)

    if all_joined:
        # Use the original chat_join_request from user_data
        join_request_update = context.user_data.get(user_id, {}).get(
            "chat_join_request"
        )
        if join_request_update:
            await query.message.delete()
            await finalize_approval(join_request_update, context)
        else:
            await query.message.edit_text(
                "Could not find original join request. Please try requesting to join the chat again."
            )
    else:
        # If they still haven't joined all channels, update the message
        await query.answer(
            "You haven't joined all the required channels yet. Please try again.",
            show_alert=True,
        )
        # Re-send the message with updated statuses
        await query.message.delete()
        # We need the original update object to pass to handle_force_sub
        join_request_update = context.user_data.get(user_id, {}).get(
            "chat_join_request"
        )
        if join_request_update:
            await handle_force_sub(join_request_update, context, user_id)


async def finalize_approval(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handles the final steps of approving a user."""
    new_member = update.effective_user
    chat_id = update.effective_chat.id

    await update.chat_join_request.approve()
    database.approved_users.insert_one({"user_id": new_member.id})
    database.stats.update_one({}, {"$inc": {"approved": 1}}, upsert=True)
    await log_message("auto_approve", user_id=new_member.id, context=context)

    if config.SEND_WELCOME_IN_CHAT:
        await context.bot.send_message(
            chat_id,
            f"Welcome {new_member.mention_html()}! Your join request has been approved.",
        )
    # Clean up user_data
    if new_member.id in context.user_data:
        del context.user_data[new_member.id]


async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles new chat join requests. It checks for bans, blacklists, and then
    triggers the force-subscribe flow if enabled.
    """
    settings = database.settings.find_one()
    if not settings or not settings.get("auto_approve_enabled", True):
        return

    new_member = update.effective_user
    if not new_member:
        return

    # Store the update object to be used later in the callback
    context.user_data[new_member.id] = {"chat_join_request": update}

    # Check if user is banned or blacklisted
    if database.banned_users.find_one(
        {"user_id": new_member.id}
    ) or database.blacklist.find_one({"user_id": new_member.id}):
        logger.info(
            f"User {new_member.id} is banned or blacklisted, declining join request."
        )
        await update.chat_join_request.decline()
        await log_message(
            "auto_decline_banned", user_id=new_member.id, context=context
        )
        return

    # If force sub is disabled, approve immediately
    if not config.FORCE_SUB_CHANNELS:
        await finalize_approval(update, context)
        return

    # Start the force-subscribe flow
    await handle_force_sub(update, context, new_member.id)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles unknown commands."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    if query.data == "help":
        await query.edit_message_text(text=user.HELP_TEXT)


def initialize_settings() -> None:
    """Initializes bot settings in the database from the config file."""
    logger.info("Initializing bot settings...")
    settings = database.settings.find_one()
    if not settings:
        database.settings.insert_one({
            "auto_approve_enabled": config.AUTO_APPROVE_INSTANT
        })
        logger.info(f"Auto-approval set to: {config.AUTO_APPROVE_INSTANT}")
    else:
        logger.info("Settings already initialized.")


def main() -> None:
    """Start the bot."""
    # --- Check for essential configurations ---
    if not all([config.BOT_TOKEN, config.API_ID, config.API_HASH, config.MONGO_URI]):
        logger.critical(
            "BOT_TOKEN, API_ID, API_HASH, and MONGO_URI must be set in the environment variables. "
            "Please check your configuration."
        )
        return

    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # User commands
    application.add_handler(CommandHandler("start", user.start))
    application.add_handler(CommandHandler("help", user.help_command))
    application.add_handler(CommandHandler("about", user.about))
    application.add_handler(CommandHandler("echo", user.echo))
    application.add_handler(CommandHandler("chatid", user.chat_id))
    application.add_handler(CommandHandler("userid", user.user_id))
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
    application.add_handler(CallbackQueryHandler(button, pattern="^help$"))
    application.add_handler(
        CallbackQueryHandler(check_join_status_callback, pattern="^check_join_status$")
    )
    application.add_handler(ChatJoinRequestHandler(auto_approve))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    initialize_settings()
    main()
