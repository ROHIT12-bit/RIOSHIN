# Telegram Auto Approval Bot

This is a Telegram bot that automatically approves new members in a chat. It also includes a variety of admin commands to manage the bot and its users.

## Features

- Auto-approval of new members
- Admin commands to manage the bot
- Blacklist and ban functionality
- Statistics and logging
- Broadcast messages to all approved users
- "Force Sub" to a channel
- Log channel for bot activities

## Deployment on Render

You can deploy this bot on Render using the provided `render.yaml` and `Dockerfile`.

1. Fork this repository.
2. Create a new "Web Service" on Render and connect it to your forked repository.
3. Set the following environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
   - `ADMIN_USER_IDS`: A comma-separated list of Telegram user IDs that should have admin access to the bot.
   - `MONGO_URI`: Your MongoDB connection string.
   - `FORCE_SUB_CHANNEL`: (Optional) The username of the channel that users must join before being approved (e.g., `@mychannel`).
   - `LOG_CHANNEL_ID`: (Optional) The ID of the channel where the bot should send log messages.
   - `START_IMAGE_URL`: (Optional) A URL to an image to be displayed in the `/start` message.

## Commands

### Public Commands

- `/start` - Start the bot
- `/help` - Show the help message
- `/about` - Show info about the bot
- `/echo <text>` - Echo back the text
- `/chatid` - Get the current chat ID
- `/userid` - Get your user ID
- `/approved` - View approved users count
- `/stats` - Bot usage & approval stats
- `/users` - Get the total number of approved users in the database
- `/banned` - View banned users list

### Admin Commands

- `/approve <user_id>` - Manually approve a user
- `/disapprove <user_id>` - Remove user approval
- `/autoapprove <on/off>` - Toggle auto-approval ON/OFF
- `/cooldown <seconds>` - Set the approval cooldown
- `/limit <count>` - Set the daily auto-approval limit
- `/blacklist <user_id>` - Add a user to the blacklist
- `/unblacklist <user_id>` - Remove a user from the blacklist
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/logs` - View approval & activity logs
- `/broadcast <message>` - Send a message to all users
