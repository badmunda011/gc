import os
import re
import requests
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from SUKH import application
from telegram.error import BadRequest

import lottie
from lottie.parsers.tgs import parse_tgs
from lottie.exporters import svg
import cairosvg

API_USER = "285702956"
API_SECRET = "bHHrSFdFdystdQJNN9xxYeCbGk6WoE5X"
API_URL = "https://api.sightengine.com/1.0/check.json"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

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
        elif file_path and os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > MAX_FILE_SIZE:
                print(f"❌ File too large: {size} bytes")
                return None
            with open(file_path, 'rb') as f:
                files = {'media': f}
                r = requests.post(API_URL, data=data, files=files, timeout=15)
        else:
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"NSFW API Error: {e}")
        return None

def convert_webp_to_png(path):
    try:
        if path.lower().endswith('.webp'):
            out = path.replace('.webp', '.png')
            Image.open(path).convert('RGB').save(out, 'PNG')
            os.remove(path)
            return out
    except Exception as e:
        print(f"WebP to PNG error: {e}")
    return path

def convert_tgs_to_png(path):
    try:
        out = path.replace('.tgs', '.png')
        animation = parse_tgs(path)
        svg_data = svg.export_svg(animation, frame=0)  # Correct for lottie>=0.6
        cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=out)
        os.remove(path)
        return out
    except Exception as e:
        print(f"TGS to PNG Error: {e}")
    return None

def extract_links(text):
    if not text:
        return []
    pattern = r'(https?://[^\s]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp|\.mp4|\.webm))'
    return re.findall(pattern, text, flags=re.IGNORECASE)

async def handle_nsfw_result(update, context, result):
    if not result or result.get("status") != "success":
        try:
            await update.message.reply_text("❌ API Error or No result.")
        except BadRequest:
            await update.effective_chat.send_message("❌ API Error or No result.")
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
    if any(v > 0.5 for v in scores.values()):
        try:
            await update.message.delete()
            await update.message.chat.send_message(
                f"🚫 NSFW Detected & Deleted!\n" +
                "\n".join(f"{k}: {v:.2f}" for k, v in scores.items())
            )
        except Exception as e:
            await update.effective_chat.send_message(f"❌ Failed to delete message: {e}")
    else:
        print(f"✅ Safe Content: {scores}")

async def nsfw_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = None
    try:
        # Download media
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_path = str(await file.download_to_drive())
        elif update.message.document:
            file = await update.message.document.get_file()
            file_path = str(await file.download_to_drive())
        elif update.message.animation:
            file = await update.message.animation.get_file()
            file_path = str(await file.download_to_drive())
        elif update.message.video:
            file = await update.message.video.get_file()
            file_path = str(await file.download_to_drive())
        elif update.message.sticker:
            file = await update.message.sticker.get_file()
            file_path = str(await file.download_to_drive())

            # Sticker Type Handling
            if update.message.sticker.is_animated and file_path.endswith('.tgs'):
                converted = convert_tgs_to_png(file_path)
                if converted:
                    file_path = converted
                else:
                    await update.message.reply_text("❌ Animated Sticker conversion failed.")
                    return
            elif update.message.sticker.is_video:
                await update.message.reply_text("❌ Video stickers not supported for NSFW scan.")
                return
            else:
                file_path = convert_webp_to_png(file_path)

        if file_path and os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in ALLOWED_EXTENSIONS and not file_path.endswith('.png'):
                await update.message.reply_text(f"⚠️ Unsupported file type: {ext}")
                return
            result = await check_nsfw(file_path=file_path)
            await handle_nsfw_result(update, context, result)

        # Also check URLs in text/caption
        links = extract_links(update.message.caption or update.message.text or "")
        for url in links:
            result = await check_nsfw(media_url=url)
            await handle_nsfw_result(update, context, result)

    except Exception as e:
        print(f"Handler Error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

async def nsfw_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    links = extract_links(update.message.text or "")
    for url in links:
        result = await check_nsfw(media_url=url)
        await handle_nsfw_result(update, context, result)

app = application
app.add_handler(MessageHandler(
    filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL | filters.Sticker.ALL,
    nsfw_media_handler
))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, nsfw_link_handler))
