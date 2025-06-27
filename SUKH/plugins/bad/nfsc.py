import os
import re
import requests
from PIL import Image
import cairosvg
from pyrogram import Client, filters
from pyrogram.types import Message
from lottie.parsers.tgs import parse_tgs
from lottie.exporters import svg as lottie_svg

from SUKH import app  # <-- As you said

API_USER = "285702956"
API_SECRET = "bHHrSFdFdystdQJNN9xxYeCbGk6WoE5X"
API_URL = "https://api.sightengine.com/1.0/check.json"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit


def convert_webp_to_png(path):
    try:
        if path.lower().endswith('.webp'):
            out = path.replace('.webp', '.png')
            Image.open(path).convert('RGB').save(out, 'PNG')
            os.remove(path)
            return out
    except Exception as e:
        print(f"WebP to PNG Error: {e}")
    return path


def convert_tgs_to_png(path):
    try:
        out = path.replace('.tgs', '.png')
        animation = parse_tgs(path)
        svg_data = lottie_svg.export_svg(animation, frame=0)  # Frame 0 export
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


async def handle_nsfw_result(message: Message, result):
    if not result or result.get("status") != "success":
        await message.reply_text("❌ API Error or No result.")
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
            await message.delete()
            await message.chat.send_text(
                f"🚫 NSFW Detected & Deleted!\n" +
                "\n".join(f"{k}: {v:.2f}" for k, v in scores.items())
            )
        except Exception as e:
            await message.reply_text(f"❌ Failed to delete message: {e}")
    else:
        print(f"✅ Safe Content: {scores}")


@app.on_message(filters.photo | filters.video | filters.animation | filters.document | filters.sticker)
async def nsfw_media_handler(client, message: Message):
    file_path = None
    try:
        media = (
            message.photo
            or message.video
            or message.animation
            or message.document
            or message.sticker
        )

        if not media:
            return

        file = await client.download_media(media)
        file_path = str(file)

        # Sticker specific handling
        if message.sticker:
            if message.sticker.is_animated and file_path.endswith('.tgs'):
                converted = convert_tgs_to_png(file_path)
                if converted:
                    file_path = converted
                else:
                    await message.reply_text("❌ Failed to convert animated sticker for scan.")
                    return
            elif message.sticker.is_video:
                await message.reply_text("❌ Video stickers not supported for NSFW scan.")
                return
            else:
                file_path = convert_webp_to_png(file_path)

        # File type check
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ALLOWED_EXTENSIONS and not file_path.endswith('.png'):
            await message.reply_text(f"⚠️ Unsupported file type: {ext}")
            return

        # Run NSFW Check
        result = await check_nsfw(file_path=file_path)
        await handle_nsfw_result(message, result)

        # Also check links in caption/text
        links = extract_links(message.caption or message.text or "")
        for url in links:
            result = await check_nsfw(media_url=url)
            await handle_nsfw_result(message, result)

    except Exception as e:
        print(f"Handler Error: {e}")
        await message.reply_text(f"❌ Error: {e}")

    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

# FIXED LINE: Exclude all command messages using regex (commands start with /)
@app.on_message(filters.text & ~filters.regex(r"^/"))
async def nsfw_link_handler(client, message: Message):
    links = extract_links(message.text or "")
    for url in links:
        result = await check_nsfw(media_url=url)
        await handle_nsfw_result(message, result)
