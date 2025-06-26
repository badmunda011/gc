import re
from pyrogram import Client, filters
from pyrogram.types import Message, User, ChatPermissions
from pyrogram.enums import ChatType, ChatMemberStatus
from config import OWNER_ID
from SUKH import app

# Warn count dictionary: {(chat_id, user_id): warn_count}
user_warns = {}

BIO_LINK_REGEX = re.compile(
    r"(?:https?://|www\.|t\.me/|telegram\.me/)[\w\-]+(?:\.[\w\-]+)*(?:[/?#][^\s]*)?",
    re.IGNORECASE,
)

# Admin check function
async def admin_check(message: Message) -> bool:
    if not message.from_user:
        return False

    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL]:
        return False

    if message.from_user.id in [
        777000,  # Telegram Service Notifications
        7436017266,  # Bot
        OWNER_ID  # Bot Owner
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

    # Check if user is admin or owner
    is_admin = await admin_check(message)
    if user.id == OWNER_ID or is_admin:
        return

    # Get latest user bio
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

        # Send warning
        try:
            await message.reply(
                f"⚠️ [{user.first_name}](tg://user?id={user.id}) ʏᴏᴜʀ ʙɪᴏ ᴄᴏɴᴛᴀɪɴs ᴀ ʟɪɴᴋ ᴡʜɪᴄʜ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!\n"
                f"ᴡᴀʀɴɪɴɢ: {warns}/5\n"
                f"ᴘʟᴇᴀsᴇ ʀᴇᴍᴏᴠᴇ ᴛʜᴇ ʟɪɴᴋ ꜰʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ. ᴀꜰᴛᴇʀ 5 ᴡᴀʀɴs, ʏᴏᴜ ᴡɪʟʟ ʙᴇ ᴍᴜᴛᴇᴅ."
            )
        except Exception as e:
            print(f"Error sending warning: {e}")

        # Notify OWNER
        try:
            username = f"@{user.username}" if user.username else f"User ID: {user.id}"
            await client.send_message(
                OWNER_ID,
                f"🚨 {username} ʜᴀs ᴀ ʟɪɴᴋ ɪɴ ʙɪᴏ ɪɴ ɢʀᴏᴜᴘ {message.chat.title} ({message.chat.id}):\n\n{user_bio}\nWarn: {warns}/5"
            )
        except Exception as e:
            print(f"Failed to notify owner: {e}")

        # Mute after 5 warns
        if warns >= 5:
            try:
                await client.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(),  # Mute (no permissions)
                )
                await message.reply(
                    f"🚫 [{user.first_name}](tg://user?id={user.id}) ʜᴀs ʙᴇᴇɴ ᴍᴜᴛᴇᴅ ᴀꜰᴛᴇʀ 5 ᴡᴀʀɴɪɴɢs!"
                )
                # Optionally reset warns after mute
                user_warns[warn_key] = 0
            except Exception as e:
                print(f"Error muting user: {e}")
