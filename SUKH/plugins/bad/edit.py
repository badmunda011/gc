from telegram import Update, Message
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode
from config import OWNER_ID
from SUKH import application, app

MAX_MESSAGE_LENGTH = 50  # Set your maximum allowed message length here
AUTHORIZED_USERS = {123456789, 987654321}  # Replace with actual authorized user IDs

async def handle_edited_message(update: Update, context: CallbackContext):
    edited_message = update.edited_message
    if edited_message:  # Removed reactions check
        chat_id = edited_message.chat_id
        message_id = edited_message.message_id
        user = edited_message.from_user

        try:
            # Delete the edited message
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

            # Send warning message
            warning_text = f"⚠️ {user.mention_html()}, ʏᴏᴜʀ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ɪs ᴛᴏᴏ ʟᴏɴɢ ᴛʜᴀᴛ's ᴡʜʏ ɪ ʜᴀᴠᴇ ᴅᴇʟᴇᴛᴇᴅ ɪᴛ."
            await context.bot.send_message(chat_id=chat_id, text=warning_text, parse_mode=ParseMode.HTML)
        
        except Exception as e:
            print(f"Failed to delete message: {e}")

async def delete_long_messages(update: Update, context: CallbackContext):
    message = update.message
    user = message.from_user

    # Skip authorized users
    if user.id in AUTHORIZED_USERS:
        return
    
    # Check if the message exceeds the maximum length
    if message.text and len(message.text.split()) > MAX_MESSAGE_LENGTH:
        try:
            # Send warning message
            warning_text = f"⚠️ {user.mention_html()}, ᴘʟᴇᴀsᴇ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ sʜᴏʀᴛ."
            await context.bot.send_message(chat_id=message.chat_id, text=warning_text, parse_mode=ParseMode.HTML)

            # Delete the long message
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
        except Exception as e:
            print(f"Failed to delete long message: {e}")

# Bot Handlers
app_instance = application
# Handler for edited messages
app_instance.add_handler(MessageHandler(filters.ALL & filters.UpdateType.EDITED, handle_edited_message))
# Handler for long messages
app_instance.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, delete_long_messages))
