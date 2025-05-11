import os
import json
from collections import defaultdict
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode
from config import OWNER_ID
from SUKH import application

AUTHORIZED_USERS_FILE = "authorized_users.json"
MAX_MESSAGE_LENGTH = 50
MESSAGE_LIMIT = 8
SPAM_DURATION = 1
SPAM_RESTRICTION_DURATION = 60

def load_authorized_users():
    if os.path.exists(AUTHORIZED_USERS_FILE):
        with open(AUTHORIZED_USERS_FILE, "r") as f:
            return set(json.load(f))
    return set(OWNER_ID)

def save_authorized_users(users):
    with open(AUTHORIZED_USERS_FILE, "w") as f:
        json.dump(list(users), f)

AUTHORIZED_USERS = load_authorized_users()
spam_tracker = defaultdict(list)

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
        await update.message.reply_text("Invalid user ID.")

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
        await update.message.reply_text("Invalid user ID.")

async def list_authorized_users(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if not AUTHORIZED_USERS:
        await update.message.reply_text("No users are currently authorized.")
        return

    authorized_users = "\n".join(map(str, AUTHORIZED_USERS))
    await update.message.reply_text(f"Authorized users:\n{authorized_users}")

async def handle_edited_message(update: Update, context: CallbackContext):
    edited_message = update.edited_message
    if edited_message:
        chat_id = edited_message.chat_id
        message_id = edited_message.message_id
        user = edited_message.from_user
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            warning_text = f"⚠️ {user.mention_html()}, ʏᴏᴜʀ ᴇᴅɪᴛᴇᴅ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ."
            await context.bot.send_message(chat_id=chat_id, text=warning_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Failed to delete message: {e}")

async def delete_long_messages(update: Update, context: CallbackContext):
    message = update.message
    user = message.from_user
    if user.id in AUTHORIZED_USERS:
        return

    if message.text and len(message.text.split()) > MAX_MESSAGE_LENGTH:
        try:
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            warning_text = f"⚠️ {user.mention_html()}, ᴘʟᴇᴀsᴇ ᴋᴇᴇᴘ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ sʜᴏʀᴛ."
            await context.bot.send_message(chat_id=message.chat_id, text=warning_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Failed to delete long message: {e}")

async def delete_links(update: Update, context: CallbackContext):
    message = update.message
    user = message.from_user
    if user.id in AUTHORIZED_USERS:
        return

    text = message.text or ""
    if any(link in text.lower() for link in ["http://", "https://", "www."]):
        try:
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            warning_text = f"⚠️ {user.mention_html()}, ʟɪɴᴋs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ."
            await context.bot.send_message(chat_id=message.chat_id, text=warning_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Failed to delete link message: {e}")

    if message.document and message.document.mime_type == "application/pdf":
        try:
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            warning_text = f"⚠️ {user.mention_html()}, ᴘᴅғ ғɪʟᴇs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ."
            await context.bot.send_message(chat_id=message.chat_id, text=warning_text, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Failed to delete PDF message: {e}")

async def antispam_handler(update: Update, context: CallbackContext):
    message = update.message
    user = message.from_user
    user_id = user.id
    if user_id in AUTHORIZED_USERS:
        return

    current_time = message.date.timestamp()
    spam_tracker[user_id].append(current_time)
    spam_tracker[user_id] = [t for t in spam_tracker[user_id] if current_time - t <= SPAM_DURATION]

    if len(spam_tracker[user_id]) > MESSAGE_LIMIT:
        try:
            await context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
            await context.bot.restrict_chat_member(
                chat_id=message.chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=int(current_time + SPAM_RESTRICTION_DURATION)
            )
            warning_text = f"⚠️ {user.mention_html()}, you have been muted for {SPAM_RESTRICTION_DURATION} seconds due to spam."
            await context.bot.send_message(chat_id=message.chat_id, text=warning_text, parse_mode=ParseMode.HTML)
            spam_tracker[user_id] = []
        except Exception as e:
            print(f"Failed to restrict spammer: {e}")

# Register handlers
app_instance = application
app_instance.add_handler(CommandHandler("auth", auth_user))
app_instance.add_handler(CommandHandler("unauth", unauth_user))
app_instance.add_handler(CommandHandler("listauth", list_authorized_users))
app_instance.add_handler(MessageHandler(filters.ALL & filters.UpdateType.EDITED, handle_edited_message))
app_instance.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, delete_long_messages))
app_instance.add_handler(MessageHandler(filters.ChatType.GROUPS, delete_links))
app_instance.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, antispam_handler))
