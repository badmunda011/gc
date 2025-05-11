from pyrogram import Client, filters
from pyrogram.types import Message
import time
from collections import defaultdict
import asyncio

# Assuming your app is defined in SUKH
from SUKH import app

# Initialize a defaultdict to store user message timestamps
user_message_times = defaultdict(list)
# Track muted users
muted_users = defaultdict(lambda: 0)

# Convert text to small caps for warnings
def to_small_caps(text):
    small_caps_map = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return text.translate(small_caps_map)

# Anti-Spam Filter
@app.on_message(filters.group & filters.text & ~filters.bot & ~filters.via_bot)
async def anti_spam(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    now = time.time()

    # Skip if user is muted
    if muted_users[(chat_id, user_id)] > now:
        try:
            await message.delete()
            return
        except Exception as e:
            print(f"Error deleting muted user message: {e}")
            return

    # Record message timestamp
    user_message_times[(chat_id, user_id)].append(now)

    # Keep only messages in the last 5 seconds
    user_message_times[(chat_id, user_id)] = [
        t for t in user_message_times[(chat_id, user_id)] if now - t <= 5
    ]

    # Spam detection: 3 or more messages in 5 seconds
    if len(user_message_times[(chat_id, user_id)]) >= 3:
        try:
            # Delete the spam message
            await message.delete()

            # Check if user was recently warned
            if len(user_message_times[(chat_id, user_id)]) < 5:
                # Send warning in small caps
                warning = to_small_caps(f"{message.from_user.mention}, stop spamming or you will be muted!")
                await message.reply_text(warning, disable_web_page_preview=True)
            else:
                # Mute user for 5 minutes
                mute_duration = 300  # 5 minutes in seconds
                muted_users[(chat_id, user_id)] = now + mute_duration

                # Restrict user (mute)
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions={
                        "can_send_messages": False,
                        "can_send_media_messages": False,
                        "can_send_polls": False,
                        "can_send_other_messages": False,
                        "can_add_web_page_previews": False
                    },
                    until_date=int(now + mute_duration)
                )

                # Notify user about mute
                mute_msg = to_small_caps(f"{message.from_user.mention}, you have been muted for 5 minutes due to spamming.")
                await message.reply_text(mute_msg, disable_web_page_preview=True)

                # Clear message times after mute
                user_message_times[(chat_id, user_id)].clear()

        except Exception as e:
            print(f"Anti-Spam Error: {e}")
    else:
        # Clean up old timestamps to prevent memory buildup
        if len(user_message_times[(chat_id, user_id)]) > 10:
            user_message_times[(chat_id, user_id)] = user_message_times[(chat_id, user_id)][-10:]

# Periodic cleanup of expired mutes
async def cleanup_muted_users():
    while True:
        now = time.time()
        expired = [(key, expiry) for key, expiry in muted_users.items() if expiry <= now]
        for key, _ in expired:
            del muted_users[key]
        await asyncio.sleep(60)  # Run every minute

