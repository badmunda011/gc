from telethon import TelegramClient, events, Button
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.errors import (
    ChatAdminRequiredError,
    UserAlreadyParticipantError,
    UserNotParticipantError,
    PhotoInvalidError,
)
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantRequest
from pymongo import MongoClient
from SUKH.misc import SUDOERS
from SUKH import Bad
from config import MONGO_DB_URI
import asyncio
import os

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
        channel_title = getattr(channel, 'title', 'Channel')
        # Fetch invite link if no username is available
        if getattr(channel, 'username', None):
            channel_link = f"https://t.me/{channel.username}"
            channel_username = f"@{channel.username}"
        else:
            try:
                full_chat = await Bad(GetFullChannelRequest(channel))
                channel_link = full_chat.full_chat.exported_invite.link
            except Exception:
                channel_link = "https://t.me/"
            channel_username = channel_link

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

        set_by_user = (f"@{event.sender.username}" if getattr(event.sender, "username", None)
                       else (getattr(event.sender, "first_name", "User")))

        await event.reply(
            message=(
                f"**🎉 Force subscription set to** [{channel_title}]({channel_username}) **for this group.**\n\n"
                f"**🆔 Channel ID:** `{channel_id}`\n"
                f"**🖇️ Channel Link:** [Get Link]({channel_link})\n"
                f"**👤 Set by:** {set_by_user}"
            ),
            file="https://envs.sh/Tn_.jpg",
            buttons=[[Button.inline("๏ Close ๏", b"close_force_sub")]]
        )
        await asyncio.sleep(1)

    except Exception as e:
        await event.reply(
            message=(
                f"**❌ Error:** `{str(e)}`\n\n"
                "**➲ Please make sure the channel is public or the bot is admin in the channel.**"
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


# --- Fix code for profile photo, name, etc. ---
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
        await Bad(GetParticipantRequest(channel_id, user_id))
        return True
    except UserNotParticipantError:
        await event.delete()
        channel_url = channel_username if channel_username.startswith("https://") else f"https://t.me/{channel_username.lstrip('@')}"

        # Get user's name and try to fetch profile photo
        try:
            user = await event.client.get_entity(user_id)
        except Exception:
            user = None

        # Name for display and hyperlink
        sender_full_name = None
        if user:
            sender_full_name = user.first_name
            if getattr(user, "last_name", None):
                sender_full_name += f" {user.last_name}"
        if not sender_full_name:
            sender_full_name = "User"

        # Try to download user's profile photo as a jpg file
        profile_pic_path = None
        temp_file = None
        try:
            temp_file = f"profile_{user_id}.jpg"
            profile_pic_path = await event.client.download_profile_photo(user, temp_file)
        except Exception:
            profile_pic_path = None

        # Decide what to send as file
        if profile_pic_path and os.path.exists(profile_pic_path):
            photo_arg = profile_pic_path
        else:
            photo_arg = "https://envs.sh/TnZ.jpg"

        # Prepare the clickable name for HTML message
        clickable_name = f"<a href='tg://user?id={user_id}'>{sender_full_name}</a>"

        await event.respond(
            message=(
                f"<b>👋 Hello {clickable_name},</b>\n\n"
                f"<b>You need to join the <a href=\"{channel_url}\">channel</a> to send messages in this group.</b>"
            ),
            file=photo_arg,
            buttons=[[Button.url("๏ Join Channel ๏", channel_url)]],
            parse_mode='html'
        )
        await asyncio.sleep(1)
        # Cleanup: delete temp profile image
        if profile_pic_path and os.path.exists(profile_pic_path):
            try:
                os.remove(profile_pic_path)
            except Exception:
                pass

    except ChatAdminRequiredError:
        forcesub_collection.delete_one({"chat_id": chat_id})
        await event.respond(
            "**🚫 I'm no longer an admin in the forced subscription channel. Force subscription has been disabled.**"
        )
        await asyncio.sleep(1)
    return False

# Enforce force subscription for group messages
@Bad.on(events.NewMessage())
async def enforce_forcesub(event):
    if event.is_group and not event.sender.bot:  # bots pe force sub na ho
        if not await check_forcesub(event):
            raise events.StopPropagation
            
