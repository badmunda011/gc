import json
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from SUKH import app  # Your bot instance

# Constants
MAX_MESSAGE_LENGTH = 40
AUTHORIZED_USERS_FILE = "authorized_users.json"
Devs = ["443809517", "7588172591"]

# Load authorized users from file
def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, "r") as f:
            return json.load(f)
    return []

AUTHORIZED_USERS = load_authorized_users()

# Delete long messages
async def delete_long_messages(client, message: Message):
    if message.from_user and message.from_user.id in AUTHORIZED_USERS + list(map(int, Devs)):
        return
    if message.text and len(message.text.split()) > MAX_MESSAGE_LENGTH:
        await message.reply_text(f"{message.from_user.mention}, ᴘʟᴇᴀsᴇ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ sʜᴏʀᴛ.")
        await message.delete()

# Delete long edited messages
async def delete_long_edited_messages(client, edited_message: Message):
    if edited_message.from_user and edited_message.from_user.id in AUTHORIZED_USERS + list(map(int, Devs)):
        return
    if edited_message.text and len(edited_message.text.split()) > 20:
        await edited_message.reply_text(f"{edited_message.from_user.mention}, ʏᴏᴜʀ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ɪs ᴛᴏᴏ ʟᴏɴɢ.")
        await edited_message.delete()

# Handlers
@app.on_message(filters.group & ~filters.me)
async def handle_messages(_, message: Message):
    await delete_long_messages(_, message)

@app.on_edited_message(filters.group & ~filters.me)
async def handle_edited_messages(_, edited_message: Message):
    await delete_long_edited_messages(_, edited_message)
