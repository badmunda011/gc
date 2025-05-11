import sys
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters
import random
import re

load_dotenv()



# ________________________________________________________________________________#
# Get it from my.telegram.org
API_ID = int(getenv("API_ID", "12380656"))
API_HASH = getenv("API_HASH", "d927c13beaaf5110f25c505b7c071273")

# ________________________________________________________________________________#
## Get it from @Botfather in Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "7332934706:AAHke648XmOaIoqv-7gigzzmGrkp8acaff0")

# ________________________________________________________________________________#
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# You have to Enter the app name which you gave to identify your  Music Bot in Heroku.
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")

# ________________________________________________________________________________#
# Database to save your chats and stats... Get MongoDB:-  https://telegra.ph/How-To-get-Mongodb-URI-04-06
DB_NAME = "BadDB"
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://bikash:bikash@bikash.3jkvhp7.mongodb.net/?retryWrites=true&w=majority")

# ________________________________________________________________________________#
# You'll need a Private Group ID for this.
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "-1002625181470"))

# ________________________________________________________________________________#

# Your User ID.
OWNER_ID = list(
    map(int, getenv("OWNER_ID", "443809517").split())
)  # Input type must be interger


# ________________________________________________________________________________#
# For customized or modified Repository

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/badmunda011/gc",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")

GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private
