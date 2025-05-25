from pyrogram.enums import ChatType
from pyrogram.types import Message
from pyrogram.handlers.edited_message_handler import EditedMessageHandler
from pyrogram import Client, filters
from SUKH import app  # Your custom Pyrogram client


async def edited_text_handler(client: Client, message: Message):
    try:
        # Ignore bot messages
        if message.from_user and message.from_user.is_bot:
            return

        # Only process in groups or supergroups
        if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
            return

        # Delete only edited text or caption messages
        if message.text or message.caption:
            await message.delete()
            print(f"Deleted edited message from {message.from_user.id if message.from_user else 'Unknown'}")

    except Exception as e:
        print(f"Error in edited_text_handler: {e}")


# Register the handler with filters
def register_edit_handler():
    handler = EditedMessageHandler(
        callback=edited_text_handler,
        filters=filters.text | filters.caption  # Only handle messages with text or captions
    )
    app.add_handler(handler)
