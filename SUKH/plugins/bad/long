from pyrogram import Client, filters
from pyrogram.types import Message
from SUKH import app  # Your bot instance

MAX_MESSAGE_LENGTH = 40  # Word limit

# Function to delete long messages
async def delete_long_messages(client, message: Message):
    if message.text and len(message.text.split()) > MAX_MESSAGE_LENGTH:
        await message.reply_text(
            f"{message.from_user.mention}, ᴘʟᴇᴀsᴇ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ sʜᴏʀᴛ."
        )
        await message.delete()

# Handler to catch all group messages
@app.on_message(filters.group & filters.text)
async def handle_messages(client, message: Message):
    await delete_long_messages(client, message)
