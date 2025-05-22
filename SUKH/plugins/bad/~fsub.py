from telethon import TelegramClient, events, Button
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.errors import (
    ChatAdminRequiredError,
    UserAlreadyParticipantError,
    UserNotParticipantError,
)
from pymongo import MongoClient
from SUKH.misc import SUDOERS
from SUKH import Bad
from config import MONGO_DB_URI
import asyncio

# MongoDB setup
fsubdb = MongoClient(MONGO_DB_URI)
forcesub_collection = fsubdb.status_db.status

# Command to set or disable force subscription
@Bad.on(events.NewMessage(pattern=r'^/fsub\b'))
async def set_forcesub(event):
    chat_id = event.chat_id
    user_id = event.sender_id

    # Check if user is a sudoer
    if user_id not in SUDOERS:
        await event.reply("**You are not a sudoer.**")
        return

    args = event.message.text.split(maxsplit=1)
    if len(args) < 2:
        await event.reply("**Usage: /fsub <channel username or ID> or /fsub off to disable**")
        return

    command = args[1].lower()

    # Disable force subscription
    if command in ["off", "disable"]:
        forcesub_collection.delete_one({"chat_id": chat_id})
        await event.reply("**Force subscription has been disabled for this group.**")
        return

    channel_input = command
    try:
        # Get channel information
        channel = await Bad.get_entity(channel_input)
        channel_id = channel.id
        channel_title = channel.title
        # Fetch invite link if no username is available
        channel_link = f"https://t.me/{channel.username}" if channel.username else (
            await Bad.invoke(GetFullChat(chat_id=channel_id))
        ).full_chat.invite_link
        channel_username = f"@{channel.username}" if channel.username else channel_link
        channel_members_count = (await Bad.get_participants(channel_id, limit=0)).total

        # Check if bot is admin in the channel
        bot_id = (await Bad.get_me()).id
        bot_is_admin = False
        async for admin in Bad.iter_participants(channel_id, filter=ChannelParticipantsAdmins):
            if admin.id == bot_id:
                bot_is_admin = True
                break

        if not bot_is_admin:
            await event.reply(
                message=(
                    "**🚫 I'm not an admin in this channel.**\n\n"
                    "**➲ Please make me an admin with:**\n\n"
                    "**➥ Invite New Members**\n\n"
                    "🛠️ **Then use /fsub <channel username> to set force subscription.**"
                ),
                file="https://envs.sh/TnZ.jpg",
                buttons=[
                    [Button.url("๏ Add me in channel ๏", f"https://t.me/{(await Bad.get_me()).username}?startchannel=s&admin=invite_users+manage_video_chats")]
                ]
            )
            await asyncio.sleep(1)
            return

        # Save force subscription settings to MongoDB
        forcesub_collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"channel_id": channel_id, "channel_username": channel_username}},
            upsert=True
        )

        # Get user who set the command
        set_by_user = f"@{event.sender.username}" if event.sender.username else event.sender.first_name

        await event.reply(
            message=(
                f"**🎉 Force subscription set to** [{channel_title}]({channel_username}) **for this group.**\n\n"
                f"**🆔 Channel ID:** `{channel_id}`\n"
                f"**🖇️ Channel Link:** [Get Link]({channel_link})\n"
                f"**📊 Member Count:** {channel_members_count}\n"
                f"**👤 Set by:** {set_by_user}"
            ),
            file="https://envs.sh/Tn_.jpg",
            buttons=[[Button.inline("๏ Close ๏", b"close_force_sub")]]
        )
        await asyncio.sleep(1)

    except Exception as e:
        await event.reply(
            message=(
                "**🚫 I'm not an admin in this channel.**\n\n"
                "**➲ Please make me an admin with:**\n\n"
                "**➥ Invite New Members**\n\n"
                "🛠️ **Then use /fsub <channel username> to set force subscription.**"
            ),
            file="https://envs.sh/TnZ.jpg",
            buttons=[
                [Button.url("๏ Add me in channel ๏", f"https://t.me/{(await Bad.get_me()).username}?startchannel=s&admin=invite_users+manage_video_chats")]
            ]
        )
        await asyncio.sleep(1)

# Handle close button
@Bad.on(events.CallbackQuery(pattern=b"close_force_sub"))
async def close_force_sub(event):
    await event.answer("Closed!")
    await event.delete()

# Check force subscription for group messages
async def check_forcesub(event):
    chat_id = event.chat_id
    user_id = event.sender_id

    # Get force subscription data
    forcesub_data = forcesub_collection.find_one({"chat_id": chat_id})
    if not forcesub_data:
        return True  # Allow if no force subscription

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data["channel_username"]

    try:
        # Check if user is a participant in the channel
        await Bad.get_participants(channel_id, filter=UserNotParticipantError(user_id))
        return True
    except UserNotParticipantError:
        # Delete user's message
        await event.delete()
        channel_url = channel_username if channel_username.startswith("https://") else f"https://t.me/{channel_username.lstrip('@')}"
        await event.reply(
            message=(
                f"**👋 Hello {event.sender.mention},**\n\n"
                f"**You need to join the [channel]({channel_url}) to send messages in this group.**"
            ),
            file="https://envs.sh/Tn_.jpg",
            buttons=[[Button.url("๏ Join Channel ๏", channel_url)]]
        )
        await asyncio.sleep(1)
    except ChatAdminRequiredError:
        # Disable force subscription if bot is no longer admin
        forcesub_collection.delete_one({"chat_id": chat_id})
        await event.reply(
            "**🚫 I'm no longer an admin in the forced subscription channel. Force subscription has been disabled.**"
        )
        await asyncio.sleep(1)
    return False

# Enforce force subscription for group messages
@Bad.on(events.NewMessage(chats=events.ChatType.GROUP))
async def enforce_forcesub(event):
    if not await check_forcesub(event):
        raise events.StopPropagation
