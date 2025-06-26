import re
from pyrogram import Client, filters
from pyrogram.types import Message, User

from config import OWNER_ID
from SUKH import app

# Powerful regex for all types of links, including Telegram links
BIO_LINK_REGEX = re.compile(
    r"(https?://|www\.)[\w\-]+(\.[\w\-]+)+([/?#][^\s]*)?|t\.me/[\w\d_]+|telegram\.me/[\w\d_]+",
    re.IGNORECASE,
)

@app.on_message(filters.all)
async def check_bio_for_links(client: Client, message: Message):
    user: User = message.from_user
    if not user:
        return

    # Fetch fresh user profile data for the bio
    try:
        user_info = await client.get_users(user.id)
        user_bio = getattr(user_info, "bio", "")
    except Exception:
        user_bio = ""

    if user_bio and BIO_LINK_REGEX.search(user_bio):
        # Warn the user
        await message.reply(
            f"⚠️ [{user.first_name}](tg://user?id={user.id}), your bio contains a link which is not allowed!",
            parse_mode="md"
        )
        # Notify the OWNER_ID for logging
        try:
            await client.send_message(
                OWNER_ID,
                f"🚨 User @{user.username or user.id} bio contains a link:\n\n{user_bio}"
            )
        except Exception as e:
            print("Failed to notify owner:", e)
