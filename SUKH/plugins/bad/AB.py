import re
from telegram import Update, User
from telegram.ext import ContextTypes, MessageHandler, filters

from config import OWNER_ID
from SUKH import application

# Powerful regex for all types of links, including Telegram links
BIO_LINK_REGEX = re.compile(
    r"(https?://|www\.)[\w\-]+(\.[\w\-]+)+([/?#][^\s]*)?|t\.me/[\w\d_]+|telegram\.me/[\w\d_]+",
    re.IGNORECASE,
)

async def check_bio_for_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.from_user is None:
        return

    user: User = update.message.from_user

    # Fetch fresh user profile data for the bio
    try:
        user_info = await context.bot.get_chat(user.id)
        user_bio = getattr(user_info, "bio", "")
    except Exception:
        user_bio = ""

    if user_bio and BIO_LINK_REGEX.search(user_bio):
        # Warn the user
        await update.message.reply_text(
            f"⚠️ {user.mention_html()}, your bio contains a link which is not allowed!",
            parse_mode="HTML",
        )
        # Notify the OWNER_ID for logging
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"🚨 User @{user.username or user.id} bio contains a link:\n\n{user_bio}"
            )
        except Exception as e:
            print("Failed to notify owner:", e)

# Register the handler in your bot
application.add_handler(MessageHandler(filters.ALL, check_bio_for_links))
