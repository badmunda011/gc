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
START_TEXT = """╭────────────────────── 
╰──● ʜɪ ɪ ᴀᴍ  ˹𝑪𝒐𝒑𝒚𝒓𝒊ɢʜᴛ ✗ 𝜝𝒐𝒕˼🤍

ғʀᴏм ᴄᴏᴘyʀιɢнт ᴘʀᴏтᴇcтιᴏɴ тᴏ ᴍᴀιɴтᴀιɴιɴɢ ᴅᴇcᴏʀυм, ᴡᴇ'vᴇ ɢᴏт ιт cᴏvᴇʀᴇᴅ. 🌙

●ɴᴏ cᴏммᴀɴᴅ, ᴊᴜѕт ᴀᴅᴅ тнιѕ ʙᴏᴛ, ᴇvᴇʀyтнιɴɢ ιѕ ᴀυтᴏ 🍁

⋆━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ
ᴍᴀᴅᴇ ᴡιтн 🖤 ʙy @II_BAD_BABY_II❣️
"""

HELP_TEXT = """💫ʜᴇʀᴇ ᴀʀᴇ sᴏᴍᴇ ᴄᴏᴍᴍᴀɴᴅs:

● **ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ**

● ᴅᴏɴ'ᴛ ᴇᴅɪᴛ ᴍsɢ sᴇɴᴅ

● ᴅᴏɴ'ᴛ ᴀɴʏ ᴅᴇᴄᴏᴍᴇɴᴛ sᴇɴᴅ

● 18+ sᴛɪᴄᴋᴇʀ ʙʟᴏᴄᴋ ᴍᴏʀᴇ sᴛɪᴄᴋᴇʀ ʙʟᴏᴄᴋ 

● ᴅᴏɴ'ᴛ 50+ ᴡᴏʀᴅs ᴍsɢ sᴇɴᴅ 

● ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴍɪɴ ɴᴏᴛ ᴀᴅᴅ ᴏᴛʜᴇʀ ʙᴏᴛ 

● ᴀɴʏ ʙᴀɴ ᴜsᴇʀ ʙᴏᴛ sᴇɴᴅ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ ɢᴄ 

● ᴀɴᴛɪ sᴘᴀᴍ + ᴀɴᴛɪ ʟɪɴᴋ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇ 

● ᴄᴜsᴛᴏᴍɪᴢᴇ ᴡᴇʟᴄᴏᴍᴇ , ᴄᴜsᴛᴏᴍɪᴢᴇ ɢᴏᴏᴅʙʏᴇ
"""

# Menu Buttons
def get_start_buttons():
    return [
        [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/JARVIS_V2"), InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ", callback_data="update")],
        [InlineKeyboardButton("ʜᴇʟᴘ", callback_data="help")]
    ]

def get_help_buttons():
    return [
        [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]
    ]

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
    reply_markup = InlineKeyboardMarkup(get_start_buttons())
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

@app.on_message(filters.command("help"))
async def help_command_handler(_, msg):
    reply_markup = InlineKeyboardMarkup(get_help_buttons())
    await msg.reply_photo(
        photo="https://files.catbox.moe/2ri8px.jpg",
        caption=HELP_TEXT,
        reply_markup=reply_markup
    )

# Callback Query Handlers
@app.on_callback_query(filters.regex("help"))
async def help_callback_handler(_, query: CallbackQuery):
    buttons = [[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_caption(
        caption=HELP_TEXT,
        reply_markup=reply_markup
    )

@app.on_callback_query(filters.regex("update"))
async def update_callback_handler(_, query: CallbackQuery):
    await query.answer("No updates available right now.", show_alert=True)

@app.on_callback_query(filters.regex("back_to_start"))
async def back_to_start_callback_handler(_, query: CallbackQuery):
    await query.message.edit_caption(
        caption=START_TEXT,
        reply_markup=InlineKeyboardMarkup(get_start_buttons())
    )

@app.on_callback_query(filters.regex("close"))
async def close_callback_handler(_, query: CallbackQuery):
    await query.message.delete()
