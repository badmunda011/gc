from SUKH import application
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters

# Welcome New Users
async def welcome(update: Update, context):
    for user in update.message.new_chat_members:
        welcome_message = f"{user.mention_html()}) • 🌸 ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ?"
        await update.message.reply_text(welcome_message, parse_mode='HTML')

# Goodbye User
async def goodbye(update: Update, context):
    user = update.message.left_chat_member
    goodbye_message = f"{user.first_name} (@{user.username if user.username else 'username'}) • 🌪️ **ɢᴏᴏᴅ ʙʏᴇ ᴛᴀᴋᴇ ᴄᴀʀᴇ**."
    await update.message.reply_text(goodbye_message, parse_mode='HTML')

# Bot Handlers
app_instance = application
app_instance.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app_instance.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye))
