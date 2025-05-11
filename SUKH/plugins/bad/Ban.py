from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
from pyrogram.handlers import ChatMemberUpdatedHandler
from SUKH import app

async def ban_change_notice(client, update: ChatMemberUpdated):
    old = update.old_chat_member
    new = update.new_chat_member
    user = new.user

    # User Banned
    if new.status == ChatMemberStatus.BANNED:
        await client.send_message(
            chat_id=update.chat.id,
            text=f"**{user.mention} ʜᴀꜱ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ.**"
        )

    # User Unbanned
    elif old.status == ChatMemberStatus.BANNED and new.status != ChatMemberStatus.BANNED:
        await client.send_message(
            chat_id=update.chat.id,
            text=f"**{user.mention} ʜᴀꜱ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ.**"
        )

app.add_handler(ChatMemberUpdatedHandler(ban_change_notice))
