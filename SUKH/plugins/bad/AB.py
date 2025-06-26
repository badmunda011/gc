import re
from pyrogram import Client, filters
from pyrogram.types import Message, User
from pyrogram.enums import ChatType, ChatMemberStatus
from config import OWNER_ID
from SUKH import app

# Warns count dict: {(chat_id, user_id): warn_count}
user_warns = {}

BIO_LINK_REGEX = re.compile(
    r"(?:https?://|www\.|t\.me/|telegram\.me/)[\w\-]+(?:\.[\w\-]+)*(?:[/?#][^\s]*)?",
    re.IGNORECASE,
)

# Admin check as you provided
async def admin_check(message: Message) -> bool:
    if not message.from_user:
        return False

    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL]:
        return False

    if message.from_user.id in [
        777000,  # Telegram Service Notifications
        7436017266,  #bot
        OWNER_ID   # Bot Owner
    ]:
        return True

    client = message._client
    chat_id = message.chat.id
    user_id = message.from_user.id

    check_status = await client.get_chat_member(chat_id=chat_id, user_id=user_id)
    if check_status.status in [
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR
    ]:
        return True
    else:
        return False

@app.on_message(filters.group & ~filters.bot & ~filters.service)
async def check_bio_for_links(client: Client, message: Message):
    user: User = message.from_user
    if not user or user.is_bot:
        return

    # Check admin/owner
    is_admin = await admin_check(message)
    if user.id == OWNER_ID or is_admin:
        return  # Owner ya admin ko ignore karo

    # Fetch fresh user profile data for the bio
    try:
        user_info = await client.get_chat(user.id)
        user_bio = getattr(user_info, "bio", "") or ""
    except Exception as e:
        print(f"Error fetching user bio: {e}")
        user_bio = ""

    if user_bio and BIO_LINK_REGEX.search(user_bio):
        warn_key = (message.chat.id, user.id)
        warns = user_warns.get(warn_key, 0) + 1
        user_warns[warn_key] = warns

        # Warn the user
        try:
            await message.reply(
                f"⚠️ [{user.first_name}](tg://user?id={user.id}), "
                f"your bio contains a link which is not allowed!\n"
                f"Warning: {warns}/5\n"
                f"Please remove the link from your bio. 5 warns ke baad aap mute ho jayenge.",
            )
        except Exception as e:
            print(f"Error sending warning: {e}")

        # Notify the OWNER_ID for logging
        try:
            username = f"@{user.username}" if user.username else f"User ID: {user.id}"
            await client.send_message(
                OWNER_ID,
                f"🚨 {username} bio contains a link in group {message.chat.title} ({message.chat.id}):\n\n{user_bio}\nWarn: {warns}/5"
            )
        except Exception as e:
            print(f"Failed to notify owner: {e}")

        # Mute user if 5 warns ho gaye
        if warns >= 5:
            try:
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=user.id,
                    permissions=None,  # Mute all permissions
                )
                await message.reply(
                    f"🚫 [{user.first_name}](tg://user?id={user.id}) ko 5 warnings ke baad mute kar diya gaya!"
                )
                # Optionally, reset warns after mute
                user_warns[warn_key] = 0
            except Exception as e:
                print(f"Error muting user: {e}")
