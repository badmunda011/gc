from pyrogram import Client, filters
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus

from SUKH import app  # Your main bot instance

@app.on_chat_member_updated(filters.group)
async def auto_kick_bot_if_added_by_non_admin(client: Client, update: ChatMemberUpdated):
    try:
        # Check if a bot was added
        if update.new_chat_member and update.new_chat_member.user.is_bot:
            added_by = update.from_user
            added_bot = update.new_chat_member.user
            chat_id = update.chat.id

            # Check if the user who added the bot is NOT an admin
            member = await client.get_chat_member(chat_id, added_by.id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                await client.kick_chat_member(chat_id, added_bot.id)
                await client.send_message(
                    chat_id,
                    f"**{added_by.mention} tried to add a bot ({added_bot.mention}) without being an admin.**\n"
                    f"The bot has been removed from the group."
                )
    except Exception as e:
        print(f"[AntiBotKick Error] {e}")
