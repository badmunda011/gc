import os
import re
import requests
from pyrogram import filters
from pyrogram.types import Message
from SUKH import app

API_USER = "285702956"
API_SECRET = "bHHrSFdFdystdQJNN9xxYeCbGk6WoE5X"
API_URL = "https://api.sightengine.com/1.0/check.json"
MODELS = "nudity-2.1,weapon,text-content"

def check_nsfw(file_path=None, media_url=None):
    data = {
        'models': MODELS,
        'api_user': API_USER,
        'api_secret': API_SECRET
    }

    try:
        if media_url:
            data['url'] = media_url
            response = requests.post(API_URL, data=data)
        elif file_path:
            with open(file_path, 'rb') as file:
                files = {'media': file}
                response = requests.post(API_URL, files=files, data=data)
        else:
            return None
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def extract_media_links(text):
    if not text:
        return []
    # Simple regex for image/video links (jpg, png, gif, mp4, webm etc.)
    pattern = r'(https?://[^\s]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp|\.mp4|\.webm))'
    return re.findall(pattern, text, flags=re.IGNORECASE)

async def handle_nsfw_response(message, result):
    if not result or result.get("status") != "success":
        return
    nudity = result.get("nudity", {})
    raw_score = nudity.get("raw", 0)
    sexual_activity_score = nudity.get("sexual_activity", 0)
    # Thresholds - adjust as needed
    if raw_score > 0.6 or sexual_activity_score > 0.5:
        await message.delete()
        await message.reply_text(
            f"🚫 NSFW Content Detected and Deleted!\n"
            f"(Raw: {raw_score}, Sexual: {sexual_activity_score})"
        )

@app.on_message(
    (filters.sticker | filters.photo | filters.video | filters.animation | filters.video_note | filters.document) & filters.group
)
async def nsfw_media_detector(client, message: Message):
    # Download media if present
    media_path = await message.download() if (message.sticker or message.photo or message.video or message.animation or message.video_note or message.document) else None

    # 1. Check for uploaded file (sticker, photo, video, etc.)
    if media_path:
        result = check_nsfw(file_path=media_path)
        await handle_nsfw_response(message, result)
        try:
            os.remove(media_path)
        except Exception:
            pass

    # 2. Check for media links in caption/text
    links = extract_media_links(message.text or "") + extract_media_links(message.caption or "")
    for url in links:
        result = check_nsfw(media_url=url)
        await handle_nsfw_response(message, result)

# Optionally, handle text messages with only links (no media attached)
@app.on_message(filters.text & filters.group)
async def nsfw_link_detector(client, message: Message):
    links = extract_media_links(message.text or "")
    for url in links:
        result = check_nsfw(media_url=url)
        await handle_nsfw_response(message, result)
