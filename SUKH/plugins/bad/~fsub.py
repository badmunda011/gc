from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pymongo import MongoClient
from SUKH import app
import asyncio
from SUKH.misc import SUDOERS
from config import MONGO_DB_URI
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import (
    ChatAdminRequired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)

fsubdb = MongoClient(MONGO_DB_URI)
forcesub_collection = fsubdb.status_db.status

@app.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def set_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Only SUDOERS can use this command now
    if user_id not in SUDOERS:
        return await message.reply_text("**ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ sᴜᴅᴏᴇʀ.**")

    if len(message.command) == 2 and message.command[1].lower() in ["off", "disable"]:
        forcesub_collection.delete_one({"chat_id": chat_id})
        return await message.reply_text("**ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**")

    if len(message.command) != 2:
        return await message.reply_text(
            "**ᴜsᴀɢᴇ: /ғsᴜʙ <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ> ᴏʀ /ғsᴜʙ ᴏғғ ᴛᴏ ᴅɪsᴀʙʟᴇ**"
        )

    channel_input = message.command[1]

    try:
        channel_info = await client.get_chat(channel_input)
        channel_id = channel_info.id
        channel_title = channel_info.title
        channel_link = await app.export_chat_invite_link(channel_id)
        channel_username = f"{channel_info.username}" if channel_info.username else channel_link
        channel_members_count = getattr(channel_info, "members_count", "N/A")

        bot_id = (await client.get_me()).id
        bot_is_admin = False

        async for admin in app.get_chat_members(channel_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if admin.user.id == bot_id:
                bot_is_admin = True
                break

        if not bot_is_admin:
            await asyncio.sleep(1)
            return await message.reply_photo(
                photo="https://envs.sh/TnZ.jpg",
                caption=(
                    "**🚫 I'ᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀɴɴᴇʟ.**\n\n"
                    "**➲ ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ᴡɪᴛʜ:**\n\n"
                    "**➥ Iɴᴠɪᴛᴇ Nᴇᴡ Mᴇᴍʙᴇʀs**\n\n"
                    "🛠️ **Tʜᴇɴ ᴜsᴇ /ғsᴜʙ <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ> ᴛᴏ sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.**"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("๏ ᴀᴅᴅ ᴍᴇ ɪɴ ᴄʜᴀɴɴᴇʟ ๏", url=f"https://t.me/{app.username}?startchannel=s&admin=invite_users+manage_video_chats")]]
                )
            )

        forcesub_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel_id": channel_id, "channel_username": channel_username}},
            upsert=True
        )

        set_by_user = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name

        await message.reply_photo(
            photo="https://envs.sh/Tn_.jpg",
            caption=(
                f"**🎉 ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛ ᴛᴏ** [{channel_title}]({channel_username}) **ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**\n\n"
                f"**🆔 ᴄʜᴀɴɴᴇʟ ɪᴅ:** `{channel_id}`\n"
                f"**🖇️ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ:** [ɢᴇᴛ ʟɪɴᴋ]({channel_link})\n"
                f"**📊 ᴍᴇᴍʙᴇʀ ᴄᴏᴜɴᴛ:** {channel_members_count}\n"
                f"**👤 sᴇᴛ ʙʏ:** {set_by_user}"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("๏ ᴄʟᴏsᴇ ๏", callback_data="close_force_sub")]]
            )
        )
        await asyncio.sleep(1)

    except Exception as e:
        await message.reply_photo(
            photo="https://envs.sh/TnZ.jpg",
            caption=(
                "**🚫 I'ᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀɴɴᴇʟ.**\n\n"
                "**➲ ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ᴡɪᴛʜ:**\n\n"
                "**➥ Iɴᴠɪᴛᴇ Nᴇᴡ Mᴇᴍʙᴇʀs**\n\n"
                "🛠️ **Tʜᴇɴ ᴜsᴇ /ғsᴜʙ <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ> ᴛᴏ sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.**"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("๏ ᴀᴅᴅ ᴍᴇ ɪɴ ᴄʜᴀɴɴᴇʟ ๏", url=f"https://t.me/{app.username}?startchannel=s&admin=invite_users+manage_video_chats")]]
            )
        )
        await asyncio.sleep(1)

@app.on_callback_query(filters.regex("close_force_sub"))
async def close_force_sub(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("ᴄʟᴏsᴇᴅ!")
    await callback_query.message.delete()

async def check_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return True  # Allow if no force sub

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data["channel_username"]

    try:
        user_member = await app.get_chat_member(channel_id, user_id)
        if user_member:
            return True
    except UserNotParticipant:
        await message.delete()
        channel_url = f"https://t.me/{channel_username}" if channel_username else (await app.export_chat_invite_link(channel_id))
        await message.reply_photo(
            photo="https://envs.sh/Tn_.jpg",
            caption=(
                f"**👋 ʜᴇʟʟᴏ {message.from_user.mention},**\n\n"
                f"**ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ]({channel_url}) ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.**"
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("๏ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ๏", url=channel_url)]])
        )
        await asyncio.sleep(1)
    except ChatAdminRequired:
        forcesub_collection.delete_one({"chat_id": chat_id})
        await message.reply_text(
            "**🚫 I'ᴍ ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ғᴏʀᴄᴇᴅ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ. ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.**"
        )
        await asyncio.sleep(1)
    return False

@app.on_message(filters.group)
async def enforce_forcesub(client: Client, message: Message):
    await check_forcesub(client, message)
