import os
import re
import requests
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from SUKH import application

# ✅ For .tgs Lottie support
import lottie
from lottie.exporters import exporters

API_USER = "285702956"
API_SECRET = "bHHrSFdFdystdQJNN9xxYeCbGk6WoE5X"
API_URL = "https://api.sightengine.com/1.0/check.json"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max

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
        elif file_path and os.path.exists(str(file_path)):
            size = os.path.getsize(str(file_path))
            if size > MAX_FILE_SIZE:
                print(f"File too large: {size}")
                return None
            with open(str(file_path), 'rb') as f:
                files = {'media': f}
                r = requests.post(API_URL, data=data, files=files, timeout=15)
        else:
            print("No valid file or URL")
            return None
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"NSFW Check Error: {e}")
        return None

def convert_webp_to_png(file_path):
    try:
        file_path = str(file_path)
        if file_path.lower().endswith('.webp'):
            out = file_path.replace('.webp', '.png')
            Image.open(file_path).convert('RGB').save(out, 'PNG')
            os.remove(file_path)
            return out
    except Exception as e:
        print(f"WebP to PNG Error: {e}")
    return str(file_path)

def convert_tgs_to_png(file_path):
    try:
        file_path = str(file_path)
        out = file_path.replace('.tgs', '.png')
        animation = lottie.parsers.tgs.parse_tgs(file_path)
        exporters.export_png(animation, out, frame=0, width=512, height=512)
        os.remove(file_path)
        return out
    except Exception as e:
        print(f"TGS to PNG Error: {e}")
    return None

def extract_links(text):
    if not text:
        return []
    pattern = r'(https?://[^\s]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp))'
    return re.findall(pattern, text, flags=re.IGNORECASE)

async def handle_nsfw_result(update, context, result):
    if not result or result.get("status") != "success":
        await update.message.reply_text("❌ API Error or No result.")
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
            await update.message.reply_text(f"❌ Delete Fail: {e}")
    else:
        print(f"Clean Content: {scores}")

async def nsfw_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_path = None
    try:
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
            if update.message.sticker.is_animated and file_path.endswith('.tgs'):
                converted = convert_tgs_to_png(file_path)
                if converted:
                    file_path = converted
                else:
                    await update.message.reply_text("❌ Failed to convert animated sticker for scan.")
                    return
            elif update.message.sticker.is_video and file_path.endswith('.webm'):
                await update.message.reply_text("❌ Video stickers not supported for NSFW scan.")
                return
            else:
                file_path = convert_webp_to_png(file_path)
        else:
            return

        if file_path and os.path.exists(file_path):
            result = await check_nsfw(file_path=file_path)
            await handle_nsfw_result(update, context, result)

        # Text links in caption
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
            except:
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
