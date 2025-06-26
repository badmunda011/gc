import os
import re
import requests
import logging
from pyrogram import filters
from pyrogram.types import Message
from PIL import Image  # For WebP to PNG conversion
from SUKH import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nsfw_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

API_USER = "285702956"
API_SECRET = "bHHrSFdFdystdQJNN9xxYeCbGk6WoE5X"
API_URL = "https://api.sightengine.com/1.0/check.json"
MODELS = "nudity-2.1,weapon,text-content"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.webm'}

def check_nsfw(file_path=None, media_url=None):
    """Send media to SightEngine API for NSFW detection."""
    data = {
        'models': MODELS,
        'api_user': API_USER,
        'api_secret': API_SECRET
    }

    try:
        if media_url:
            data['url'] = media_url
            logger.info(f"Checking NSFW for URL: {media_url}")
            response = requests.post(API_URL, data=data, timeout=10)
        elif file_path:
            logger.info(f"Checking NSFW for file: {file_path}")
            with open(file_path, 'rb') as file:
                files = {'media': file}
                response = requests.post(API_URL, files=files, data=data, timeout=10)
        else:
            logger.error("No file path or URL provided for NSFW check")
            return None

        response.raise_for_status()  # Raise exception for bad status codes
        result = response.json()
        logger.info(f"API Response: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected Error in check_nsfw: {e}")
        return None

def convert_webp_to_png(file_path):
    """Convert WebP file to PNG for SightEngine compatibility."""
    try:
        if file_path.lower().endswith('.webp'):
            png_path = file_path.rsplit('.', 1)[0] + '.png'
            with Image.open(file_path) as img:
                img.convert('RGB').save(png_path, 'PNG')
            logger.info(f"Converted WebP to PNG: {png_path}")
            os.remove(file_path)  # Remove original WebP
            return png_path
        return file_path
    except Exception as e:
        logger.error(f"Error converting WebP to PNG: {e}")
        return None

def extract_media_links(text):
    """Extract media links from text."""
    if not text:
        return []
    pattern = r'(https?://[^\s]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp|\.mp4|\.webm))'
    links = re.findall(pattern, text, flags=re.IGNORECASE)
    logger.info(f"Extracted media links: {links}")
    return links

async def handle_nsfw_response(message: Message, result):
    """Handle NSFW detection response and take action."""
    if not result or result.get("status") != "success":
        logger.error(f"Invalid API response: {result}")
        await message.reply_text("⚠️ Error checking NSFW content. Please try again.", quote=True)
        return

    nudity = result.get("nudity", {})
    # Use multiple nudity metrics for better detection
    scores = {
        'sexual_activity': nudity.get('sexual_activity', 0),
        'sexual_display': nudity.get('sexual_display', 0),
        'erotica': nudity.get('erotica', 0),
        'very_suggestive': nudity.get('very_suggestive', 0),
        'suggestive': nudity.get('suggestive', 0)
    }
    logger.info(f"Nudity scores: {scores}")

    # Adjust thresholds based on API response structure
    if any(score > 0.5 for score in scores.values()):
        try:
            await message.delete()
            await message.reply_text(
                f"🚫 NSFW Content Detected and Deleted!\n"
                f"Scores: {', '.join(f'{k}: {v:.2f}' for k, v in scores.items())}"
            )
            logger.info(f"Deleted message {message.id} due to NSFW content")
        except Exception as e:
            logger.error(f"Error deleting message {message.id}: {e}")
            await message.reply_text("⚠️ NSFW content detected, but failed to delete.", quote=True)
    else:
        logger.info(f"Message {message.id} is safe (Scores: {scores})")

@app.on_message(
    (filters.sticker | filters.photo | filters.video | filters.animation | filters.video_note | filters.document) & filters.group
)
async def nsfw_media_detector(client, message: Message):
    """Detect NSFW content in media messages."""
    media_path = None
    try:
        # Download media if present
        if message.sticker or message.photo or message.video or message.animation or message.video_note or message.document:
            media_path = await message.download()
            if not media_path:
                logger.error(f"Failed to download media for message {message.id}")
                await message.reply_text("⚠️ Error downloading media for NSFW check.", quote=True)
                return

            # Check file extension
            file_ext = os.path.splitext(media_path)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                logger.warning(f"Unsupported file extension {file_ext} for message {message.id}")
                os.remove(media_path)
                return

            # Convert WebP stickers to PNG
            if message.sticker and file_ext == '.webp':
                media_path = convert_webp_to_png(media_path)
                if not media_path:
                    logger.error(f"Failed to convert WebP sticker for message {message.id}")
                    return

            # Check NSFW for downloaded file
            result = check_nsfw(file_path=media_path)
            await handle_nsfw_response(message, result)

        # Check media links in caption/text
        links = extract_media_links(message.text or "") + extract_media_links(message.caption or "")
        for url in links:
            result = check_nsfw(media_url=url)
            await handle_nsfw_response(message, result)

    except Exception as e:
        logger.error(f"Error in nsfw_media_detector for message {message.id}: {e}")
        await message.reply_text("⚠️ Error processing media for NSFW check.", quote=True)
    finally:
        # Clean up downloaded file
        if media_path and os.path.exists(media_path):
            try:
                os.remove(media_path)
                logger.info(f"Cleaned up file: {media_path}")
            except Exception as e:
                logger.error(f"Error cleaning up file {media_path}: {e}")

@app.on_message(filters.text & filters.group)
async def nsfw_link_detector(client, message: Message):
    """Detect NSFW content in text messages with media links."""
    try:
        links = extract_media_links(message.text or "")
        for url in links:
            result = check_nsfw(media_url=url)
            await handle_nsfw_response(message, result)
    except Exception as e:
        logger.error(f"Error in nsfw_link_detector for message {message.id}: {e}")
        await message.reply_text("⚠️ Error checking links for NSFW content.", quote=True)
