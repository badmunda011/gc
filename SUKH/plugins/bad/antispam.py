from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
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
            await message.chat.send_message(warning)
        except Exception as e:
            print("Link Deletion Error:", e)

# Anti-PDF Filter
@app.on_message(filters.group & filters.document)
async def anti_pdf(_, message: Message):
    if message.document and message.document.file_name.endswith(".pdf"):
        try:
            await message.delete()
            warning = to_small_caps(f"{message.from_user.mention} files are not allowed.")
            await message.chat.send_message(warning)
        except Exception as e:
            print("PDF Deletion Error:", e)

# Anti-Spam Filter
@app.on_message(filters.group & filters.text)
async def anti_spam(_, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    now = time.time()

    user_message_times[(chat_id, user_id)].append(now)

    # Keep only messages in last 2 seconds
    user_message_times[(chat_id, user_id)] = [
        t for t in user_message_times[(chat_id, user_id)] if now - t <= 3
    ]

    if len(user_message_times[(chat_id, user_id)]) >= 2:
        try:
            # Mute user for 60 seconds
            await app.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(),
                until_date=int(time.time()) + 60
            )
            warning = to_small_caps(f"{message.from_user.mention}, you are muted for spamming for 60 seconds.")
            await message.chat.send_message(warning)
            user_message_times[(chat_id, user_id)] = []  # Reset after mute
        except Exception as e:
            print("Mute Error:", e)
