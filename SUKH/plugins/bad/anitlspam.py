from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from datetime import datetime, timedelta

from SUKH import app

flood_count = {}
FLOOD_LIMIT = 6
FLOOD_TIMER = 3  # in seconds
FLOOD_ACTION_DURATION = 60  # in seconds

# Check if user is admin
async def is_admin(client, message: Message):
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except:
        return False

# Check if sender is admin (decorator-like usage)
def adminsOnly(func):
    async def wrapper(client, message):
        if not await is_admin(client, message):
            return
        return await func(client, message)
    return wrapper

# /flood command to show flood info
@app.on_message(filters.command("flood") & filters.group)
@adminsOnly
async def flood_info(c, m: Message):
    await m.reply(
        f"**AntiFlood Active:**\n"
        f"Flood Limit: `{FLOOD_LIMIT}` messages\n"
        f"Timer Window: `{FLOOD_TIMER}` seconds\n"
        f"Action: `Temporary Mute` for `{FLOOD_ACTION_DURATION}` seconds"
    )

# Automatic flood detection
@app.on_message(filters.group, group=31)
async def detect_flood(c: Client, m: Message):
    try:
        user_id = m.from_user.id
        chat_id = m.chat.id

        member = await c.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return

        flood_count.setdefault(chat_id, {}).setdefault(user_id, {"count": 0, "first": datetime.now()})
        data = flood_count[chat_id][user_id]
        now = datetime.now()

        if (now - data["first"]).seconds > FLOOD_TIMER:
            data["count"] = 1
            data["first"] = now
        else:
            data["count"] += 1

        if data["count"] > FLOOD_LIMIT:
            until_date = now + timedelta(seconds=FLOOD_ACTION_DURATION)
            await c.restrict_chat_member(
                chat_id,
                user_id,
                ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            await m.reply(f"ᴜsᴇʀ {m.from_user.mention} ꜰʟᴏᴏᴅᴇᴅ ᴛʜᴇ ᴄʜᴀᴛ ᴀɴᴅ ᴡᴀꜱ ᴍᴜᴛᴇᴅ ꜰᴏʀ 1 ᴍɪɴᴜᴛᴇ.")
            data["count"] = 0  # Reset after action

    except Exception as e:
        print(f"[FLOOD ERROR] {e}")
