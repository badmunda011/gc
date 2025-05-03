import time
import config 
import logging
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler(),
    ],
)

LOGGERR = logging.getLogger(__name__)
boot = time.time()
mongodb = MongoCli(config.MONGO_DB_URI)
db = mongodb.Anonymous
mongo = MongoClient(config.MONGO_DB_URI)
OWNER = config.OWNER_ID
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
