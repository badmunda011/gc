from pyrogram import Client, filters
from pyrogram.types import Message
import re
import time
from collections import defaultdict
from SUKH import app

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
          
