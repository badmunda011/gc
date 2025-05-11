import os
import json
from collections import defaultdict
from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode
from config import OWNER_ID
from SUKH import application

AUTHORIZED_USERS_FILE = "authorized_users.json"
MAX_MESSAGE_LENGTH = 50  # Set your maximum allowed message length here
MESSAGE_LIMIT = 8  # Maximum messages allowed within SPAM_DURATION
SPAM_DURATION = 1  # Time duration to monitor for spam in seconds
SPAM_RESTRICTION_DURATION = 60  # Restriction time in seconds

# Load authorized users from file
def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, "r") as f:
            return set(json.load(f))
    return {OWNER_ID}

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

# Function to delete long messages
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

# Function to delete messages containing links
async def delete_links(update: Update, context: CallbackContext):
    message = update.message
    user = message.from_user

    # Skip authorized users
    if user.id in AUTHORIZED_USERS:
        return

    if message.text and ("http://" in message.text or "https://" in message.text or "www." in message.text):
        try:
            # Delete the message with a link
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            warning_text = f"⚠️ {user.mention_html()}, ʟɪɴᴋs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ."
            await context.bot.send_message(chat_id=message.chat_id, text=warning_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Failed to delete link message: {e}")

# Function to handle spam
async def antispam_handler(update: Update, context: CallbackContext):
    message = update.message
    user_id = message.from_user.id
    current_time = message.date.timestamp()

    # Add current message timestamp to the user's record
    spam_tracker[user_id].append(current_time)

    # Remove timestamps older than SPAM_DURATION
    spam_tracker[user_id] = [
        t for t in spam_tracker[user_id] if current_time - t <= SPAM_DURATION
    ]

    if len(spam_tracker[user_id]) > MESSAGE_LIMIT:
        try:
            # Restrict user for SPAM_RESTRICTION_DURATION
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            warning_text = f"⚠️ Too many messages in a short time. You are restricted for {SPAM_RESTRICTION_DURATION} seconds."
            await context.bot.send_message(chat_id=message.chat_id, text=warning_text, parse_mode=ParseMode.HTML)

            # Clear spam tracker for the user
            spam_tracker[user_id] = []
        except Exception as e:
            print(f"Failed to handle spam: {e}")

# Bot Handlers
app_instance = application
# Command handlers for authorization
app_instance.add_handler(CommandHandler("auth", auth_user))
app_instance.add_handler(CommandHandler("unauth", unauth_user))
app_instance.add_handler(CommandHandler("listauth", list_authorized_users))
# Handler for edited messages
app_instance.add_handler(MessageHandler(filters.ALL & filters.UpdateType.EDITED, handle_edited_message))
# Handler for long messages
app_instance.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, delete_long_messages))
# Handler for detecting links
app_instance.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, delete_links))
# Handler for spam detection
app_instance.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, antispam_handler))
