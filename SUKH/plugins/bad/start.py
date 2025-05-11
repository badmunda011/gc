import logging
import os
import platform
import psutil
import time
import json

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import BOT_USERNAME, OWNER_ID
from SUKH import app
from config import *

# Constants
START_TEXT = """<b>🤖 ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ 🛡️</b>

ʜᴇʏ ᴛʜɪs ɪs ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛᴏʀ ʀᴏʙᴏᴛ 🤖\n
ᴡᴇ ᴇɴsᴜʀᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ's sᴇᴄᴜʀɪᴛʏ 📌\n
ᴛʜɪs ʙᴏᴛ ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ʟᴏɴɢ ᴇᴅɪᴛᴇᴅ ᴛᴇxᴛs ᴀɴᴅ ᴄᴏᴘʏʀɪɢʜᴛᴇᴅ ᴍᴀᴛᴇʀɪᴀʟ 📁\n
ᴊᴜsᴛ ᴀᴅᴅ ᴛʜɪs ʙᴏᴛ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ɪᴛ ᴀɴ ᴀᴅᴍɪɴ\n
ғᴇᴇʟ ғʀᴇᴇ ғʀᴏᴍ ᴀɴʏ ᴛʏᴘᴇ ᴏғ **ᴄᴏᴘʏʀɪɢʜᴛ** 🛡️
"""

# Define gd_buttons
gd_buttons = [
    [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/JARVIS_V2"),
     InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="back_to_start"),
     InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/JARVIS_V_SUPPORT")]
]

# Bot Functionality
start_time = time.time()

# Utility functions
def time_formatter(milliseconds: float) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

def size_formatter(bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            break
        bytes /= 1024.0
    return f"{bytes:.2f} {unit}"

# Command Handlers
@app.on_message(filters.command("start"))
async def start_command_handler(_, msg):
    buttons = [
        [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("• ʜᴀɴᴅʟᴇʀ •", callback_data="vip_back")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await msg.reply_photo(
        photo="https://files.catbox.moe/2ri8px.jpg",
        caption=START_TEXT,
        reply_markup=reply_markup
    )

@app.on_message(filters.command("ping"))
async def activevc(_, message: Message):
    uptime = time_formatter((time.time() - start_time) * 1000)
    cpu = psutil.cpu_percent()
    storage = psutil.disk_usage('/')
    python_version = platform.python_version()

    reply_text = (
        f"➪ᴜᴘᴛɪᴍᴇ: {uptime}\n"
        f"➪ᴄᴘᴜ: {cpu}%\n"
        f"➪ꜱᴛᴏʀᴀɢᴇ: {size_formatter(storage.total)} [ᴛᴏᴛᴀʟ]\n"
        f"➪{size_formatter(storage.used)} [ᴜsᴇᴅ]\n"
        f"➪{size_formatter(storage.free)} [ғʀᴇᴇ]\n"
        f"➪ᴊᴀʀᴠɪs ᴠᴇʀsɪᴏɴ: {python_version}"
    )
    await message.reply(reply_text, quote=True)


# Callback Query Handlers
@app.on_callback_query(filters.regex("vip_back"))
async def vip_back_callback_handler(_, query: CallbackQuery):
    await query.message.edit_caption(caption=START_TEXT, reply_markup=InlineKeyboardMarkup(gd_buttons))

@app.on_callback_query(filters.regex("back_to_start"))
async def back_to_start_callback_handler(_, query: CallbackQuery):
    await query.answer()
    await query.message.delete()
    await start_command_handler(_, query.message)
    
