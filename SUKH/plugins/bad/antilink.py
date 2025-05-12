from pyrogram import Client, filters
from pyrogram.types import Message
import re
from collections import defaultdict
from SUKH import app

# Regex for link detection
LINK_REGEX = r"(https?://\S+|www\.\S+|\S+\.(com|in|net|org|info|xyz))"

# User spam tracking
user_message_times = defaultdict(list)

# Anti-Link Filter
@app.on_message(filters.group & filters.text & ~filters.private)
async def anti_link(_, message: Message):
    if re.search(LINK_REGEX, message.text.lower()):
        try:
            await message.delete()
            warning = f"{message.from_user.mention} ʟɪɴᴋꜱ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ."
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
                warning = f"{message.from_user.mention} ꜰɪʟᴇꜱ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ."
                await message.reply_text(warning)  # Use reply_text instead of send_message
    except Exception as e:
        print("File Deletion Error:", e)
