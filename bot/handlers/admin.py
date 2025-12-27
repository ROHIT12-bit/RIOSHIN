from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from bot import config, database
from bot.logging import log_message

def admin_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.ADMIN_USER_IDS:
            await update.message.reply_text("You are not authorized to use this command.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

@admin_only
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manually approve a user."""
    try:
        user_id = int(context.args[0])
        database.approved_users.insert_one({"user_id": user_id})
        database.stats.update_one({}, {"$inc": {"approved": 1}}, upsert=True)
        await log_message("approve", user_id=user_id, details=f"Approved by {update.effective_user.id}", context=context)
        await update.message.reply_text(f"User {user_id} has been approved.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /approve <user_id>")


@admin_only
async def disapprove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove user approval."""
    try:
        user_id = int(context.args[0])
        result = database.approved_users.delete_one({"user_id": user_id})
        if result.deleted_count > 0:
            database.stats.update_one({}, {"$inc": {"disapproved": 1}}, upsert=True)
            await log_message("disapprove", user_id=user_id, details=f"Disapproved by {update.effective_user.id}", context=context)
            await update.message.reply_text(f"User {user_id} has been disapproved.")
        else:
            await update.message.reply_text("User not found in the approved list.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /disapprove <user_id>")


@admin_only
async def auto_approve_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Toggle auto-approval ON/OFF."""
    try:
        status = context.args[0].lower()
        if status == "on":
            database.settings.update_one({}, {"$set": {"auto_approve_enabled": True}}, upsert=True)
            await log_message("auto_approve_toggle", details="Auto-approval enabled", context=context)
            await update.message.reply_text("Auto-approval has been enabled.")
        elif status == "off":
            database.settings.update_one({}, {"$set": {"auto_approve_enabled": False}}, upsert=True)
            await log_message("auto_approve_toggle", details="Auto-approval disabled", context=context)
            await update.message.reply_text("Auto-approval has been disabled.")
        else:
            await update.message.reply_text("Usage: /autoapprove <on/off>")
    except IndexError:
        await update.message.reply_text("Usage: /autoapprove <on/off>")


@admin_only
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ban a user."""
    try:
        user_id = int(context.args[0])
        database.banned_users.insert_one({"user_id": user_id})
        database.approved_users.delete_one({"user_id": user_id})
        database.stats.update_one({}, {"$inc": {"banned": 1}}, upsert=True)
        await log_message("ban", user_id=user_id, details=f"Banned by {update.effective_user.id}", context=context)
        await update.message.reply_text(f"User {user_id} has been banned.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /ban <user_id>")


@admin_only
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unban a user."""
    try:
        user_id = int(context.args[0])
        result = database.banned_users.delete_one({"user_id": user_id})
        if result.deleted_count > 0:
            database.stats.update_one({}, {"$inc": {"unbanned": 1}}, upsert=True)
            await log_message("unban", user_id=user_id, details=f"Unbanned by {update.effective_user.id}", context=context)
            await update.message.reply_text(f"User {user_id} has been unbanned.")
        else:
            await update.message.reply_text("User not found in the banned list.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /unban <user_id>")


@admin_only
async def set_cooldown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the approval cooldown period."""
    try:
        cooldown = int(context.args[0])
        database.settings.update_one({}, {"$set": {"cooldown_period": cooldown}}, upsert=True)
        await log_message("set_cooldown", details=f"Cooldown set to {cooldown} seconds", context=context)
        await update.message.reply_text(f"Approval cooldown has been set to {cooldown} seconds.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /cooldown <seconds>")


@admin_only
async def set_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set the daily auto-approval limit."""
    try:
        limit = int(context.args[0])
        database.settings.update_one({}, {"$set": {"daily_approval_limit": limit}}, upsert=True)
        await log_message("set_limit", details=f"Daily limit set to {limit}", context=context)
        await update.message.reply_text(f"Daily auto-approval limit has been set to {limit}.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /limit <count>")


@admin_only
async def blacklist_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a user to the blacklist."""
    try:
        user_id = int(context.args[0])
        database.blacklist.insert_one({"user_id": user_id})
        database.approved_users.delete_one({"user_id": user_id})
        database.stats.update_one({}, {"$inc": {"blacklisted": 1}}, upsert=True)
        await log_message("blacklist", user_id=user_id, details=f"Blacklisted by {update.effective_user.id}", context=context)
        await update.message.reply_text(f"User {user_id} has been blacklisted.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /blacklist <user_id>")


@admin_only
async def unblacklist_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove a user from the blacklist."""
    try:
        user_id = int(context.args[0])
        result = database.blacklist.delete_one({"user_id": user_id})
        if result.deleted_count > 0:
            database.stats.update_one({}, {"$inc": {"unblacklisted": 1}}, upsert=True)
            await log_message("unblacklist", user_id=user_id, details=f"Unblacklisted by {update.effective_user.id}", context=context)
            await update.message.reply_text(f"User {user_id} has been unblacklisted.")
        else:
            await update.message.reply_text("User not found in the blacklist.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /unblacklist <user_id>")


@admin_only
async def view_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View approval & activity logs."""
    logs = database.logs.find().sort("timestamp", -1).limit(20)
    if logs:
        log_messages = []
        for log in logs:
            log_messages.append(f"Action: {log['action']}, User ID: {log.get('user_id', 'N/A')}, Details: {log.get('details', 'N/A')}, Timestamp: {log['timestamp']}")
        await update.message.reply_text(f"Recent Logs:\n" + "\n".join(log_messages))
    else:
        await update.message.reply_text("No log entries.")


@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message to all users."""
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    approved_users = database.approved_users.find()
    for user in approved_users:
        try:
            await context.bot.send_message(chat_id=user["user_id"], text=message)
        except Exception as e:
            print(f"Failed to send message to {user['user_id']}: {e}")

    database.stats.update_one({}, {"$inc": {"broadcasts": 1}}, upsert=True)
    await log_message("broadcast", details=f"Broadcast sent by {update.effective_user.id}", context=context)
    await update.message.reply_text("Broadcast sent to all approved users.")
