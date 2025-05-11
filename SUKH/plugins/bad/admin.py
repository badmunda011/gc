from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
from pyrogram.handlers import ChatMemberUpdatedHandler
from SUKH import app

def get_status(status):
    return {
        ChatMemberStatus.ADMINISTRATOR: "ᴀᴅᴍɪɴ",
        ChatMemberStatus.MEMBER: "ᴍᴇᴍʙᴇʀ",
        ChatMemberStatus.OWNER: "ᴏᴡɴᴇʀ"
    }.get(status, status)

async def admin_change_notice(client, update: ChatMemberUpdated):
    old = update.old_chat_member
    new = update.new_chat_member
    user = new.user

    # Promoted to admin
    if old.status != ChatMemberStatus.ADMINISTRATOR and new.status == ChatMemberStatus.ADMINISTRATOR:
        await update.chat.send_message(
            f"**{user.mention} ɪꜱ ɴᴏᴡ ᴀɴ {get_status(new.status).upper()} ᴏꜰ ᴛʜɪꜱ ɢʀᴏᴜᴘ.**"
        )

    # Demoted from admin
    elif old.status == ChatMemberStatus.ADMINISTRATOR and new.status != ChatMemberStatus.ADMINISTRATOR:
        await update.chat.send_message(
            f"**{user.mention} ɪꜱ ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ.**"
        )

app.add_handler(ChatMemberUpdatedHandler(admin_change_notice))
