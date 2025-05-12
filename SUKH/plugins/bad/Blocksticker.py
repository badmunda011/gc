from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
from SUKH import app
from SUKH.misc import SUDOERS
from config import MONGO_DB_URI as MONGO_URL

client = MongoClient(MONGO_URL)
db = client["StickerBlocker"]
blocked = db["blocked_packs"]

# /addblock
@app.on_message(filters.command("addblock") & SUDOERS)
async def add_sticker_block(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker = message.reply_to_message.sticker
        if not blocked.find_one({"type": "sticker", "id": sticker.file_unique_id}):
            blocked.insert_one({"type": "sticker", "id": sticker.file_unique_id})
            await message.reply("Sticker has been blocked.")
        else:
            await message.reply("Sticker is already blocked.")
    elif len(message.command) > 1:
        link = message.command[1]
        if "addstickers" in link or "stickers" in link:
            pack_id = link.split("/")[-1]
            if not blocked.find_one({"type": "pack", "id": pack_id}):
                blocked.insert_one({"type": "pack", "id": pack_id})
                await message.reply("Sticker pack has been blocked.")
            else:
                await message.reply("Pack is already blocked.")
        else:
            await message.reply("Invalid pack link.")
    else:
        await message.reply("Reply to a sticker or send a pack link.")

# /unblock
@app.on_message(filters.command("unblock") & SUDOERS)
async def unblock_sticker(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker = message.reply_to_message.sticker
        result = blocked.delete_one({"type": "sticker", "id": sticker.file_unique_id})
        if result.deleted_count:
            await message.reply("Sticker has been unblocked.")
        else:
            await message.reply("Sticker was not blocked.")
    elif len(message.command) > 1:
        link = message.command[1]
        if "addstickers" in link or "stickers" in link:
            pack_id = link.split("/")[-1]
            result = blocked.delete_one({"type": "pack", "id": pack_id})
            if result.deleted_count:
                await message.reply("Sticker pack has been unblocked.")
            else:
                await message.reply("Pack was not blocked.")
        else:
            await message.reply("Invalid pack link.")
    else:
        await message.reply("Reply to a sticker or send a pack link.")

# /unblockall
@app.on_message(filters.command("unblockall") & SUDOERS)
async def unblock_all(client: Client, message: Message):
    result = blocked.delete_many({})
    await message.reply(f"Unblocked all. Total removed: `{result.deleted_count}`")

# /stickerid
@app.on_message(filters.command("stickerid") & SUDOERS)
async def show_sticker_info(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.sticker:
        sticker = message.reply_to_message.sticker
        info = f"**Sticker Info:**\n"
        info += f"• File Unique ID: `{sticker.file_unique_id}`\n"
        if sticker.set_name:
            info += f"• Pack: [{sticker.set_name}](https://t.me/addstickers/{sticker.set_name})"
        else:
            info += "• Pack: `Unknown`"
        await message.reply(info)
    else:
        await message.reply("Reply to a sticker to get its info.")

# /listblocks
@app.on_message(filters.command("listblocks") & SUDOERS)
async def list_blocked_items(client: Client, message: Message):
    items = list(blocked.find())
    if not items:
        return await message.reply("No blocked stickers or packs.")

    text = "**Blocked Stickers & Packs:**\n"
    for i, item in enumerate(items, 1):
        if item["type"] == "sticker":
            text += f"{i}. Sticker ID: `{item['id']}`\n"
        elif item["type"] == "pack":
            text += f"{i}. Pack: [Link](https://t.me/addstickers/{item['id']})\n"
    await message.reply(text)

# Auto delete + warn user
@app.on_message(filters.sticker & filters.group, group=999)
async def auto_delete_blocked(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in SUDOERS:
        return  # Allow SUDO to send any sticker

    sticker = message.sticker
    sid = sticker.file_unique_id
    sname = sticker.set_name

    if blocked.find_one({"type": "sticker", "id": sid}) or \
       (sname and blocked.find_one({"type": "pack", "id": sname})):
        await message.delete()
        name = message.from_user.mention
        # Fix: Use the client to send a message to the chat
        await client.send_message(
            chat_id=message.chat.id,
            text=f"**{name}**, ᴘʟᴇᴀꜱᴇ ᴅᴏɴ’ᴛ ꜱᴇɴᴅ 18+ ꜱᴛɪᴄᴋᴇʀꜱ."
        )
