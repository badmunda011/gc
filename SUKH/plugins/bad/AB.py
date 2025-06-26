import re
from pyrogram import Client, filters
from pyrogram.types import Message, User
from config import OWNER_ID
from SUKH import app

# Powerful regex for all types of links, including Telegram links
BIO_LINK_REGEX = re.compile(
    r"(?:https?://|www\.|t\.me/|telegram\.me/)[\w\-]+(?:\.[\w\-]+)*(?:[/?#][^\s]*)?",
    re.IGNORECASE,
)

@app.on_message(filters.private | filters.group & ~filters.bot & ~filters.service)
async def check_bio_for_links(client: Client, message: Message):
    user: User = message.from_user
    if not user or user.is_bot:
        return

    # Fetch fresh user profile data for the bio
    try:
        user_info = await client.get_chat(user.id)
        user_bio = getattr(user_info, "bio", "") or ""
    except Exception as e:
        print(f"Error fetching user bio: {e}")
        user_bio = ""

    if user_bio and BIO_LINK_REGEX.search(user_bio):
        # Warn the user
        try:
            await message.reply(
                f"⚠️ [{user.first_name}](tg://user?id={user.id}), your bio contains a link which is not allowed!",
            )
        except Exception as e:
            print(f"Error sending warning: {e}")

        # Notify the OWNER_ID for logging
        try:
            username = f"@{user.username}" if user.username else f"User ID: {user.id}"
            await client.send_message(
                OWNER_ID,
                f"🚨 {username} bio contains a link:\n\n{user_bio}"
            )
        except Exception as e:
            print(f"Failed to notify owner: {e}")
