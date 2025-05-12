from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode
from SUKH import application

# Function to handle long messages
async def handle_long_message(update: Update, context: CallbackContext):
    message: Message = update.message
    if message and len(message.text.split()) > 60:  # Check if the message has more than 50 words
        try:
            chat_id = message.chat_id
            message_id = message.message_id
            user = message.from_user

            # Delete the message
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

            # Send warning message
            warning_text = f"⚠️ {user.mention_html()}, ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ ᴇxᴄᴇᴇᴅꜱ 60 ᴡᴏʀᴅꜱ ᴀɴᴅ ʜᴀꜱ ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ."
            await context.bot.send_message(chat_id=chat_id, text=warning_text, parse_mode=ParseMode.HTML)

        except Exception as e:
            print(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇꜱꜱᴀɢᴇ: {e}")

# Create the application instance
app_instance = application
# Add the message handler for long messages
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_long_message))
