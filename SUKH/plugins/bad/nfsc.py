from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
import requests
from SUKH import application

API_USER = "285702956"
API_SECRET = "bHHrSFdFdystdQJNN9xxYeCbGk6WoE5X"
API_URL = "https://api.sightengine.com/1.0/check.json"

async def check_nsfw(file_path):
    with open(file_path, 'rb') as f:
        files = {'media': f}
        data = {
            'models': 'nudity-2.1',
            'api_user': API_USER,
            'api_secret': API_SECRET
        }
        r = requests.post(API_URL, files=files, data=data)
        return r.json()

async def nsfw_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        file_path = await file.download_to_drive()
        result = await check_nsfw(file_path)
        await update.message.reply_text(str(result))
        os.remove(file_path)

app_instance = application
app_instance.add_handler(MessageHandler(filters.PHOTO, nsfw_handler))
