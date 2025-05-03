from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode 
from AviaxMusic import application

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
            warning_text = f"⚠️ {user.mention_html()}, editing messages is not allowed."
            await context.bot.send_message(chat_id=chat_id, text=warning_text, parse_mode=ParseMode.HTML)
        
        except Exception as e:
            print(f"Failed to delete message: {e}")

# Bot Handlers
app_instance = application
app_instance.add_handler(MessageHandler(filters.ALL & filters.UpdateType.EDITED, handle_edited_message))
