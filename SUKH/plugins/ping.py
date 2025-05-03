from pyrogram import filters
from pyrogram.types import Message
import time
from SUKH import app

@app.on_message(filters.command(["ping", "alive"]))
async def ping(_, message: Message):
    start_time = time.time()
    sent_message = await message.reply_text("Pinging...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 3)
    await sent_message.edit_text(f"Pong! 🏓\nResponse time: {ping_time} ms")
