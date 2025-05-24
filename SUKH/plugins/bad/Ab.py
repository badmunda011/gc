import requests
from pyrogram import filters
from pyrogram.types import Message
from SUKH import app  # Apni custom Client import

# Sightengine API keys
API_USER = "53095053"  # Replace with your user ID
API_SECRET = "AbjrhdugRaPyat6F9efgGdtK6Z3uCDaz"  # Replace with your secret key

# Blocked classes: porn, drugs, weapons, etc.
BLOCKED_CLASSES = ["nudity", "weapon", "alcohol", "drugs", "tobacco"]

# Main function to check sticker
def is_sticker_blocked(file_url: str) -> bool:
    response = requests.get(
        "https://api.sightengine.com/1.0/check.json",
        params={
            "url": file_url,
            "models": "nudity,wad,offensive,face-attributes",
            "api_user": API_USER,
            "api_secret": API_SECRET,
        },
    )
    result = response.json()

    # Debug print
    print(result)

    # Check for high probability in blocked content
    try:
        if result.get("nudity", {}).get("raw", 0) > 0.4:
            return True
        if result.get("weapon", 0) > 0.4:
            return True
        if result.get("alcohol", 0) > 0.4:
            return True
        if result.get("drugs", 0) > 0.4:
            return True
        if result.get("tobacco", 0) > 0.4:
            return True
    except Exception as e:
        print(f"Error while checking sticker: {e}")
        pass
    return False

@app.on_message(filters.sticker)
async def check_sticker(app, message: Message):
    try:
        if not hasattr(message, "sticker") or message.sticker is None:
            print("No sticker found in the message.")
            return
        file = await app.get_file(message.sticker.file_id)
        file_url = f"https://api.telegram.org/file/bot{app.token}/{file.file_path}"
        # Check content using Sightengine
        if is_sticker_blocked(file_url):
            await message.delete()
            await message.reply("**Sticker blocked due to NSFW**")
