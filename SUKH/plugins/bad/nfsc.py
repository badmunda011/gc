import os
import requests
from pyrogram import filters
from pyrogram.types import Message
from SUKH import app

API_USER = "285702956"
API_SECRET = "bHHrSFdFdystdQJNN9xxYeCbGk6WoE5X"

def check_nsfw(file_path):
    url = "https://api.sightengine.com/1.0/check.json"
    files = {'media': open(file_path, 'rb')}
    data = {
        'models': 'nudity-2.1,weapon,text-content',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }

    try:
        response = requests.post(url, files=files, data=data)
        result = response.json()
        return result
    except Exception as e:
        print(f"API Error: {e}")
        return None
    finally:
        files['media'].close()

@app.on_message(filters.sticker & filters.group)
async def nsfw_sticker_detector(client, message: Message):
    sticker_path = await message.download()

    if not sticker_path:
        return

    result = check_nsfw(sticker_path)

    # Optional: Delete file after check
    if os.path.exists(sticker_path):
        os.remove(sticker_path)

    if not result:
        return

    try:
        # Example: Check for porn or sexual activity
        nudity = result.get("nudity", {})
        raw_score = nudity.get("raw", 0)
        sexual_activity_score = nudity.get("sexual_activity", 0)

        # Threshold: You can adjust these
        if raw_score > 0.6 or sexual_activity_score > 0.5:
            await message.delete()
            await message.reply_text(
                f"🚫 NSFW Sticker Detected and Deleted!\n"
                f"(Raw: {raw_score}, Sexual: {sexual_activity_score})"
            )
    except Exception as e:
        print(f"Detection parse error: {e}")
