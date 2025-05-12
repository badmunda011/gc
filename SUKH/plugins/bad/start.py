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
from SUKH.misc import SUDOERS  # Importing SUDOERS for sudo-only commands
from config import *

# Global Variables
start_time = time.time()  # Initialize start_time to track bot uptime
total_users_count = 0  # Example placeholder for total users count
total_chats_count = 0  # Example placeholder for total chats count

# Constants
START_TEXT = """<blockquote>╭────────────────────── 
╰──● ʜɪ ɪ ᴀᴍ  ˹𝑪𝒐𝒑𝒚ʀɪɢʜᴛ ✗ 𝜝𝒐𝒕˼🤍<blockquote>

<blockquote>ғʀᴏм ᴄᴏᴘʏʀιɢнт ᴘʀᴏтᴇcтιᴏɴ тᴏ ᴍᴀιɴтᴀιɴιɴɢ ᴅᴇcᴏʀυм, ᴡᴇ'vᴇ ɢᴏт ιт cᴏvᴇʀᴇᴅ. 🌙<blockquote>

<blockquote>●ɴᴏ cᴏммᴀɴᴅ, ᴊᴜѕт ᴀᴅᴅ тнιѕ ʙᴏт, ᴇvᴇʀyтнιɴɢ ιѕ ᴀυтᴏ 🍁<blockquote>

<blockquote>⋆━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄<blockquote>
<blockquote>ᴍᴀᴅᴇ ᴡιтн 🖤 ʙy @II_BAD_BABY_II❣️<blockquote>
"""

HELP_TEXT = """💫ʜᴇʀᴇ ᴀʀᴇ sᴏᴍᴇ ᴄᴏᴍᴍᴀɴᴅs:

● **ᴄᴏᴘʏʀɪɢʜᴛ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ**

● ᴘɪɴɢ  ᴄʜᴇᴄᴋ ʙᴏᴛ's ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ.

● ᴅᴏɴ'ᴛ ᴇᴅɪᴛ ᴍsɢ sᴇɴᴅ.

● ᴅᴏɴ'ᴛ ᴀɴʏ ᴅᴇᴄᴏᴍᴇɴᴛ sᴇɴᴅ.

● 18+ sᴛɪᴄᴋᴇʀ ʙʟᴏᴄᴋ ᴍᴏʀᴇ sᴛɪᴄᴋᴇʀ ʙʟᴏᴄᴋ.

● ᴅᴏɴ'ᴛ 50+ ᴡᴏʀᴅs ᴍsɢ sᴇɴᴅ.

● ᴡɪᴛʜᴏᴜᴛ ᴀᴅᴍɪɴ ɴᴏᴛ ᴀᴅᴅ ᴏᴛʜᴇʀ ʙᴏᴛ.

● ᴀɴʏ ʙᴀɴ ᴜsᴇʀ ʙᴏᴛ sᴇɴᴅ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ɪɴ ɢᴄ.

● ᴀɴᴛɪ sᴘᴀᴍ + ᴀɴᴛɪ ʟɪɴᴋ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅᴇʟᴇᴛᴇ. 

● ᴄᴜsᴛᴏᴍɪᴢᴇ ᴡᴇʟᴄᴏᴍᴇ , ᴄᴜsᴛᴏᴍɪᴢᴇ ɢᴏᴏᴅʙʏᴇ.
"""

# Menu Buttons
def get_start_buttons():
    return [
        [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/I_AM_SIDHU"), InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇ", url="https://t.me/HEROKUBIN_01")],
        [InlineKeyboardButton("ʜᴇʟᴘ", callback_data="help")]
    ]

def get_help_buttons(is_direct_command=False):
    if is_direct_command:
        return [[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]]
    else:
        return [[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back_to_start")]]

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
        photo="https://files.catbox.moe/x4d0nd.jpg",
        caption=START_TEXT,
        reply_markup=reply_markup
    )

@app.on_message(filters.command("help"))
async def help_command_handler(_, msg):
    reply_markup = InlineKeyboardMarkup(get_help_buttons(is_direct_command=True))
    await msg.reply_photo(
        photo="https://files.catbox.moe/x4d0nd.jpg",
        caption=HELP_TEXT,
        reply_markup=reply_markup
    )

# Callback Query Handlers
@app.on_callback_query(filters.regex("help"))
async def help_callback_handler(_, query: CallbackQuery):
    buttons = get_help_buttons(is_direct_command=False)
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_caption(
        caption=HELP_TEXT,
        reply_markup=reply_markup
    )

@app.on_callback_query(filters.regex("back_to_start"))
async def back_to_start_callback_handler(_, query: CallbackQuery):
    await query.message.edit_caption(
        caption=START_TEXT,
        reply_markup=InlineKeyboardMarkup(get_start_buttons())
    )

@app.on_callback_query(filters.regex("close"))
async def close_callback_handler(_, query: CallbackQuery):
    await query.message.delete()

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
        f"➪ᴘʙx ᴠᴇʀsɪᴏɴ: {python_version}"
    )
    await message.reply(reply_text, quote=True)


# New Stats Command (Sudo-Only)
@app.on_message(filters.command("stats") & SUDOERS)
async def stats_command_handler(_, message: Message):
    stats_text = (
        f"📊 **ʙᴏᴛ sᴛᴀᴛs**\n"
        f"➪ ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘ {total_chats_count}\n"
        f"➪ ᴛᴏᴛᴀʟ ᴜsᴇʀ {total_users_count}\n"
    )
    await message.reply(stats_text, quote=True)
