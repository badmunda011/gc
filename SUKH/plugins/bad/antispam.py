from pyrogram import Client, filters
from pyrogram.types import Message
import re
import time
from collections import defaultdict
from SUKH import app

# Regex for link detection
LINK_REGEX = r"(https?://\S+|www\.\S+|\S+\.(com|in|net|org|info|xyz))"

# User spam tracking
user_message_times = defaultdict(list)

# Small caps converter
def to_small_caps(text: str) -> str:
    normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    table = str.maketrans(normal, small)
    return text.translate(table)

# Anti-Link Filter
@app.on_message(filters.group & filters.text & ~filters.private)
async def anti_link(_, message: Message):
    if re.search(LINK_REGEX, message.text.lower()):
        try:
            await message.delete()
            warning = to_small_caps(f"{message.from_user.mention} links are not allowed.")
            await message.reply_text(warning)  # Use reply_text instead of send_message
        except Exception as e:
            print("Link Deletion Error:", e)

# Anti-File Filter
@app.on_message(filters.group & filters.document)
async def anti_files(_, message: Message):
    allowed_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4')
    blocked_extensions = tuple(f".{chr(c)}" for c in range(97, 123) if f".{chr(c)}" not in allowed_extensions)

    try:
        file_name = message.document.file_name.lower()
        if not file_name.endswith(allowed_extensions):
            # Block all files except allowed ones
            if file_name.endswith(blocked_extensions) or "." in file_name:
                await message.delete()
                warning = to_small_caps(f"{message.from_user.mention} files are not allowed.")
                await message.reply_text(warning)  # Use reply_text instead of send_message
    except Exception as e:
        print("File Deletion Error:", e)

# Anti-Spam Filter
@app.on_message(filters.group & filters.text)
async def anti_spam(_, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    now = time.time()

    user_message_times[(chat_id, user_id)].append(now)

    # Keep only messages in the last 3 seconds
    user_message_times[(chat_id, user_id)] = [
        t for t in user_message_times[(chat_id, user_id)] if now - t <= 3
    ]

    if len(user_message_times[(chat_id, user_id)]) >= 2:
        try:
            # Delete the user's message instead of muting
            await message.delete()
            warning = to_small_caps(f"{message.from_user.mention}, please avoid spamming.")
            await message.reply_text(warning)  # Use reply_text instead of send_message
            user_message_times[(chat_id, user_id)] = []  # Reset after warning
        except Exception as e:
            print("Spam Deletion Error:", e)
