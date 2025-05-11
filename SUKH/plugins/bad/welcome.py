import time
from SUKH import application
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters
from pymongo import MongoClient
from config import MONGO_DB_URI as MONGO_URL

# MongoDB Connection
client = MongoClient(MONGO_URL)
db = client['telegram_bot']
collection = db['messages']

# /welcomehelp command function
async def welcome_help(update: Update, context: CallbackContext):
    help_text = """<b>Fillings</b>

You can also customise the contents of your message with contextual data. For example, you could mention a user by name in the welcome message, or mention them in a filter!

<b>Supported fillings:</b>
- <code>{first}</code>: The user's first name.
- <code>{last}</code>: The user's last name.
- <code>{fullname}</code>: The user's full name.
- <code>{username}</code>: The user's username. If they don't have one, mentions the user instead.
- <code>{mention}</code>: Mentions the user with their firstname.
- <code>{id}</code>: The user's ID.
- <code>{chatname}</code>: The chat's name.

<b>Example usages:</b>
- Save a filter using the user's name.
  ➜ <code>/filter test {first} triggered this filter.</code>

- Add a rules button to a note.
  ➜ <code>/save info Press the button to read the chat rules! {rules}</code>

- Mention a user in the welcome message.
  ➜ <code>/setwelcome Welcome {mention} to {chatname}!</code>
    """
    
    await update.message.reply_text(help_text, parse_mode="HTML")

# Function to parse buttons properly
def parse_buttons(text):
    buttons = []
    lines = text.split("\n")
    remaining_text_lines = []

    for line in lines:
        if line.startswith("[") and "](" in line and "buttonurl://" in line:
            try:
                parts = line.split("](")
                button_text = parts[0][1:].strip()
                button_url = parts[1].replace("buttonurl://", "").replace(")", "").strip()

                if button_url.startswith("@"):
                    button_url = f"https://t.me/{button_url[1:]}"

                buttons.append({"text": button_text, "url": button_url})
            except IndexError:
                remaining_text_lines.append(line)
        else:
            remaining_text_lines.append(line)

    cleaned_text = "\n".join(remaining_text_lines).strip()
    
    return buttons, cleaned_text

# Function to build keyboard buttons
def build_keyboard(buttons_data):
    if not buttons_data:
        return None

    buttons = [InlineKeyboardButton(text=btn["text"], url=btn["url"]) for btn in buttons_data]
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]  # 2 buttons per row

    return InlineKeyboardMarkup(keyboard)

# Function to format placeholders correctly
def format_message(user, chat, message_template):
    formatted_message = message_template.format(
        first=user.first_name or '',
        last=user.last_name or '',
        fullname=(user.first_name + ' ' + (user.last_name or '')).strip(),
        username=f"@{user.username}" if user.username else user.first_name,
        mention=user.mention_html() or '',
        id=user.id,
        chatname=chat.title or ''
    )

    return formatted_message.replace("{name}", "").strip()

# Check if user is admin
async def is_admin(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

# Set Welcome Message
async def set_welcome(update: Update, context: CallbackContext):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ You must be an admin to set the welcome message.")
        return

    if update.message.reply_to_message:
        raw_message = update.message.reply_to_message.caption or update.message.reply_to_message.text
    elif context.args:
        raw_message = ' '.join(context.args)
    else:
        await update.message.reply_text("⚠ Please provide a welcome message.")
        return

    buttons, welcome_message = parse_buttons(raw_message)
    media = None

    if update.message.reply_to_message:
        if update.message.reply_to_message.photo:
            media = update.message.reply_to_message.photo[-1].file_id
        elif update.message.reply_to_message.video:
            media = update.message.reply_to_message.video.file_id

    collection.update_one(
        {'chat_id': update.message.chat_id},
        {'$set': {'welcome_message': welcome_message, 'welcome_media': media, 'welcome_buttons': buttons}},
        upsert=True
    )
    await update.message.reply_text("✅ Welcome message set!")

# Welcome New Users
async def welcome(update: Update, context: CallbackContext):
    if collection.find_one({'chat_id': update.message.chat_id, 'welcome_disabled': True}):
        return
    
    data = collection.find_one({'chat_id': update.message.chat_id})
    
    for user in update.message.new_chat_members:
        welcome_message = data.get('welcome_message', "Welcome to the group, {first}!")
        formatted_message = format_message(user, update.message.chat, welcome_message)

        buttons_data = data.get('welcome_buttons', [])
        keyboard = build_keyboard(buttons_data)

        media = data.get('welcome_media')
        if media:
            try:
                await update.message.reply_photo(photo=media, caption=formatted_message, parse_mode='HTML', reply_markup=keyboard)
            except:
                await update.message.reply_video(video=media, caption=formatted_message, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.message.reply_text(formatted_message, parse_mode='HTML', reply_markup=keyboard)
            

# Set Goodbye Message
async def set_goodbye(update: Update, context: CallbackContext):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ You must be an admin to set the goodbye message.")
        return

    if update.message.reply_to_message:
        raw_message = update.message.reply_to_message.caption or update.message.reply_to_message.text
    elif context.args:
        raw_message = ' '.join(context.args)
    else:
        await update.message.reply_text("⚠ Please provide a goodbye message.")
        return

    buttons, goodbye_message = parse_buttons(raw_message)
    media = None

    if update.message.reply_to_message:
        if update.message.reply_to_message.photo:
            media = update.message.reply_to_message.photo[-1].file_id
        elif update.message.reply_to_message.video:
            media = update.message.reply_to_message.video.file_id

    collection.update_one(
        {'chat_id': update.message.chat_id},
        {'$set': {'goodbye_message': goodbye_message, 'goodbye_media': media, 'goodbye_buttons': buttons}},
        upsert=True
    )
    await update.message.reply_text("✅ Goodbye message set!")

# Goodbye User
async def goodbye(update: Update, context: CallbackContext):
    user = update.message.left_chat_member
    data = collection.find_one({'chat_id': update.message.chat_id})

    goodbye_message = data.get('goodbye_message', "Goodbye, {first}!")
    formatted_message = format_message(user, update.message.chat, goodbye_message)

    buttons_data = data.get('goodbye_buttons', [])
    keyboard = build_keyboard(buttons_data)

    media = data.get('goodbye_media')
    if media:
        try:
            await update.message.reply_photo(photo=media, caption=formatted_message, parse_mode='HTML', reply_markup=keyboard)
        except:
            await update.message.reply_video(video=media, caption=formatted_message, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.message.reply_text(formatted_message, parse_mode='HTML', reply_markup=keyboard)

# Disable Welcome Message
async def disable_welcome(update: Update, context: CallbackContext):
    collection.update_one({'chat_id': update.message.chat_id}, {'$set': {'welcome_disabled': True}}, upsert=True)
    await update.message.reply_text("Welcome message disabled.")

# ✅ **Show Welcome Message**
async def show_welcome(update: Update, context: CallbackContext):
    data = collection.find_one({'chat_id': update.message.chat_id})
    if not data or 'welcome_message' not in data:
        await update.message.reply_text("⚠ No welcome message set.")
    else:
        await update.message.reply_text(f"📝 <b>Current Welcome Message:</b>\n{data['welcome_message']}", parse_mode="HTML")
        

# Show Goodbye Message
async def show_goodbye(update: Update, context: CallbackContext):
    data = collection.find_one({'chat_id': update.message.chat_id})
    if not data or 'goodbye_message' not in data:
        await update.message.reply_text("⚠ No goodbye message set.")
    else:
        await update.message.reply_text(f"📝 <b>Current Goodbye Message:</b>\n{data['goodbye_message']}", parse_mode="HTML")

# Bot Handlers
app_instance = application
app_instance.add_handler(CommandHandler("setwelcome", set_welcome))
app_instance.add_handler(CommandHandler("setgoodbye", set_goodbye))
app_instance.add_handler(CommandHandler("disablewelcome", disable_welcome))
app_instance.add_handler(CommandHandler("showwelcome", show_welcome))
app_instance.add_handler(CommandHandler("showgoodbye", show_goodbye))
app_instance.add_handler(CommandHandler("welcomehelp", welcome_help))
app_instance.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app_instance.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye))
