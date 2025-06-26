import os
import re
import requests
from PIL import Image
from telegram import Update
from SUKH import application
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

API_USER = "285702956"
API_SECRET = "bHHrSFdFdystdQJNN9xxYeCbGk6WoE5X"
API_URL = "https://api.sightengine.com/1.0/check.json"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm', '.mkv', '.mov'}

async def check_nsfw(file_path=None, media_url=None):
    data = {
        'models': 'nudity-2.1',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }
    try:
        if media_url:
            data['url'] = media_url
            r = requests.post(API_URL, data=data, timeout=15)
        elif file_path:
            with open(file_path, 'rb') as f:
                files = {'media': f}
                r = requests.post(API_URL, data=data, files=files, timeout=15)
        else:
            return None
        return r.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def convert_webp_to_png(file_path):
    try:
        if file_path.lower().endswith('.webp'):
            png_path = file_path.rsplit('.', 1)[0] + '.png'
            with Image.open(file_path) as img:
                img.convert('RGB').save(png_path, 'PNG')
            os.remove(file_path)
            return png_path
    except Exception as e:
        print(f"WebP Conversion Error: {e}")
    return file_path

def extract_links(text):
    if not text:
        return []
    pattern = r'(https?://[^\s]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp|\.mp4|\.webm|\.mkv|\.mov))'
    return re.findall(pattern, text, flags=re.IGNORECASE)

async def handle_nsfw_result(update, context, result):
    if not result or result.get("status") != "success":
        await update.message.reply_text("❌ NSFW API Error or No Result.")
        return

    nudity = result.get("nudity", {})
    scores = {
        'sexual_activity': nudity.get('sexual_activity', 0),
        'sexual_display': nudity.get('sexual_display', 0),
        'erotica': nudity.get('erotica', 0),
        'very_suggestive': nudity.get('very_suggestive', 0),
        'suggestive': nudity.get('suggestive', 0),
        'mildly_suggestive': nudity.get('mildly_suggestive', 0)
    }

    threshold = 0.5
    if any(score > threshold for score in scores.values()):
        try:
            await update.message.delete()
            await update.message.chat.send_message(
                f"🚫 NSFW Content Deleted!\n"
                f"Scores:\n" + "\n".join(f"{k}: {v:.2f}" for k, v in scores.items())
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to delete NSFW message: {e}")
    else:
        await update.message.reply_text(
            "✅ Content Safe:\n" + "\n".join(f"{k}: {v:.2f}" for k, v in scores.items())
        )

async def nsfw_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = None
    try:
        # Handle Photo
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_path = await file.download_to_drive()

        # Handle Video
        elif update.message.video:
            file = await update.message.video.get_file()
            file_path = await file.download_to_drive()

        # Handle Animation (GIF)
        elif update.message.animation:
            file = await update.message.animation.get_file()
            file_path = await file.download_to_drive()

        # Handle Document (Any type)
        elif update.message.document:
            file = await update.message.document.get_file()
            file_path = await file.download_to_drive()

        # Handle Sticker (convert WebP)
        elif update.message.sticker:
            file = await update.message.sticker.get_file()
            file_path = await file.download_to_drive()
            file_path = convert_webp_to_png(file_path)

        # If file downloaded
        if file_path and os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                result = await check_nsfw(file_path=file_path)
                await handle_nsfw_result(update, context, result)
            else:
                await update.message.reply_text(f"⚠️ Unsupported file type: {ext}")

        # Check URLs in captions/text
        links = extract_links(update.message.caption or "")
        for url in links:
            result = await check_nsfw(media_url=url)
            await handle_nsfw_result(update, context, result)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

async def nsfw_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        links = extract_links(update.message.text or "")
        for url in links:
            result = await check_nsfw(media_url=url)
            await handle_nsfw_result(update, context, result)
    except Exception as e:
        await update.message.reply_text(f"❌ Error checking links: {e}")

app_instance = application
# Handlers
app_instance.add_handler(MessageHandler(
    filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL | filters.Sticker.ALL, nsfw_media_handler))

app_instance.add_handler(MessageHandler(filters.TEXT, nsfw_link_handler))
