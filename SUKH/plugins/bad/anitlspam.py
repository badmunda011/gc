import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
from SUKH import application

from telegram import Update, ChatPermissions
from telegram.constants import ChatAction
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Spam tracking: user_id -> deque of timestamps
user_message_log = defaultdict(lambda: deque(maxlen=10))
# Mute tracking: user_id -> mute_until datetime
muted_users = {}

# Configurable thresholds
SPAM_MSG_COUNT = 8
SPAM_TIME_SECONDS = 2
MUTE_DURATION = 60  # in seconds

async def anti_spam_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = message.from_user
    user_id = user.id
    chat_id = message.chat_id

    # Ignore admins
    member = await context.bot.get_chat_member(chat_id, user_id)
    if member.status in ("administrator", "creator"):
        return

    now = datetime.now()

    # Check if user is muted
    if user_id in muted_users:
        if datetime.now() < muted_users[user_id]:
            await context.bot.delete_message(chat_id, message.message_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{user.mention_html()}, please wait, you're temporarily muted.",
                parse_mode="HTML"
            )
            return
        else:
            del muted_users[user_id]  # Unmute user automatically

    # Track message timestamps
    user_message_log[user_id].append(now)

    # Check spam condition
    if len(user_message_log[user_id]) >= SPAM_MSG_COUNT:
        time_diff = (now - user_message_log[user_id][0]).total_seconds()
        if time_diff <= SPAM_TIME_SECONDS:
            # Mute user for 1 minute
            mute_until = now + timedelta(seconds=MUTE_DURATION)
            muted_users[user_id] = mute_until

            try:
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    permissions=ChatPermissions(can_send_messages=False),
                    until_date=mute_until
                )

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ {user.mention_html()} is muted for spamming (1 minute).",
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Failed to mute user: {e}")
                
                
# Bot Handlers
app_instance = application            
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam_handler))
