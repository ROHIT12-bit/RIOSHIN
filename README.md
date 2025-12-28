# Telegram Auto Approval Bot

This is a Telegram bot that automatically approves new members in a chat. It was made by Rohit from BotsKingdoms. It also includes a variety of admin commands to manage the bot and its users.

## Features

- Auto-approval of new members
- Admin commands to manage the bot
- Blacklist and ban functionality
- Statistics and logging
- Broadcast messages to all approved users
- "Force Sub" to a channel
- Log channel for bot activities
- Highly customizable through a configuration file

## Configuration

The bot's behavior is controlled by variables in `bot/config.py`. For security, sensitive credentials **must** be set as environment variables. Other settings can be edited directly in the file or overridden with environment variables for flexibility during deployment.

### Sensitive Variables (Must be Environment Variables)

- `BOT_TOKEN`: Your Telegram bot token from @BotFather.
- `API_ID`: Your API ID from https://my.telegram.org.
- `API_HASH`: Your API Hash from https://my.telegram.org.
- `MONGO_URI`: Your MongoDB connection string.
- `ADMIN_USER_IDS`: A comma-separated list of Telegram user IDs that should have admin access to the bot (e.g., `12345678,98765432`).

### General Configuration (Optional Environment Variables)

You can edit these in `bot/config.py` or set them as environment variables.

- `OWNER_USERNAME`: The username of the bot owner (e.g., `@BOTSKINGDOMS`).
- `FORCE_SUB_CHANNELS`: A comma-separated list of channel usernames (without '@') that users must join. The bot will check up to the first 5 channels. (e.g., `channel1,channel2,channel3`).
- `AUTO_APPROVE_INSTANT`: Set to `True` to enable auto-approval on startup, `False` otherwise.
- `SEND_WELCOME_IN_CHAT`: Set to `True` to send a welcome message in the chat after approving a user.
- `WELCOME_IMAGE`: A URL to an image to be displayed in the `/start` message.
- `FOOTER`: A footer text to be included in messages like `/start` and `/help`.
- `MAIN_CHANNEL`: The URL for the "Main Channel" button in the start message.
- `SUPPORT_LINK`: The URL for the "Support Group" button in the start message.
- `LOG_CHAT_ID`: The chat ID of the channel where the bot should send log messages.

## Deployment on Render

You can deploy this bot on Render using the provided `render.yaml` and `Dockerfile`.

1.  Fork this repository.
2.  Create a new "Web Service" on Render and connect it to your forked repository. Render will automatically use `render.yaml` for setup.
3.  In the "Environment" section, add the **Sensitive Variables** listed above.
4.  (Optional) Add any of the **General Configuration** variables to the environment to override the defaults in `bot/config.py`.

## Commands

### Public Commands

- `/start` - Start the bot
- `/help` - Show the help message
- `/about` - Show info about the bot
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
