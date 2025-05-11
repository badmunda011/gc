import os
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from collections import defaultdict
from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode
from config import OWNER_ID
from SUKH import application, app

AUTHORIZED_USERS_FILE = "authorized_users.json"

# Load authorized users from file
def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, "r") as f:
            return set(json.load(f))
    return set(OWNER_ID)  # Convert list of owner IDs to a set

# Save authorized users to file
def save_authorized_users(users):
    with open(AUTHORIZED_USERS_FILE, "w") as f:
        json.dump(list(users), f)

AUTHORIZED_USERS = load_authorized_users()
spam_tracker = defaultdict(list)  # Tracks messages per user

# Command to authorize a user
async def auth_user(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /auth <user_id>")
        return

    try:
        user_id = int(context.args[0])
        if user_id not in AUTHORIZED_USERS:
            AUTHORIZED_USERS.add(user_id)
            save_authorized_users(AUTHORIZED_USERS)
            await update.message.reply_text(f"User {user_id} has been authorized.")
        else:
            await update.message.reply_text(f"User {user_id} is already authorized.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a numeric user ID.")

# Command to unauthorize a user
async def unauth_user(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /unauth <user_id>")
        return

    try:
        user_id = int(context.args[0])
        if user_id in AUTHORIZED_USERS:
            AUTHORIZED_USERS.remove(user_id)
            save_authorized_users(AUTHORIZED_USERS)
            await update.message.reply_text(f"User {user_id} has been unauthorized.")
        else:
            await update.message.reply_text(f"User {user_id} is not authorized.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a numeric user ID.")

# Command to list all authorized users
async def list_authorized_users(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not AUTHORIZED_USERS:
        await update.message.reply_text("No users are currently authorized.")
        return

    authorized_users = "\n".join(map(str, AUTHORIZED_USERS))
    await update.message.reply_text(f"Authorized users:\n{authorized_users}")

# Function to handle edited messages
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
            warning_text = f"⚠️ {user.mention_html()}, ʏᴏᴜʀ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ."
            await context.bot.send_message(chat_id=chat_id, text=warning_text, parse_mode=ParseMode.HTML)
        
        except Exception as e:
            print(f"Failed to delete message: {e}")



# Delete long messages
async def delete_long_messages(client, message: Message):
    if message.from_user and message.from_user.id in AUTHORIZED_USERS + list(map(int, Devs)):
        return
    if message.text and len(message.text.split()) > MAX_MESSAGE_LENGTH:
        await message.reply_text(f"{message.from_user.mention}, ᴘʟᴇᴀsᴇ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ sʜᴏʀᴛ.")
        await message.delete()

# Delete long edited messages
async def delete_long_edited_messages(client, edited_message: Message):
    if edited_message.from_user and edited_message.from_user.id in AUTHORIZED_USERS + list(map(int, Devs)):
        return
    if edited_message.text and len(edited_message.text.split()) > 20:
        await edited_message.reply_text(f"{edited_message.from_user.mention}, ʏᴏᴜʀ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ɪs ᴛᴏᴏ ʟᴏɴɢ.")
        await edited_message.delete()

# Handlers
@app.on_message(filters.group & ~filters.me)
async def handle_messages(_, message: Message):
    await delete_long_messages(_, message)

@app.on_edited_message(filters.group & ~filters.me)
async def handle_edited_messages(_, edited_message: Message):
    await delete_long_edited_messages(_, edited_message)


# Bot Handlers
app_instance = application
# Command handlers for authorization
app_instance.add_handler(CommandHandler("auth", auth_user))
app_instance.add_handler(CommandHandler("unauth", unauth_user))
app_instance.add_handler(CommandHandler("listauth", list_authorized_users))
# Handler for edited messages
app_instance.add_handler(MessageHandler(filters.ALL & filters.UpdateType.EDITED, handle_edited_message))
