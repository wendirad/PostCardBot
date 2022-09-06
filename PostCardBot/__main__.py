"""PostCardBot - Telegram bot for sending postcards."""
import asyncio

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.mongo import MongoStorage

from loguru import logger

from PostCardBot.core import config
from PostCardBot.core.utils import load_handlers

# Setup the storage for states
storage = MongoStorage(
    uri=config.DATABASE_URL, db_name=config.STORAGE_DATABASE_NAME
)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# Setup the middleware
for middleware in config.middlewares:
    dp.middleware.setup(middleware)

# Register handlers
load_handlers(bot, dp)

logger.info("Bot start polling")
executor.start_polling(dp, skip_updates=True)

asyncio.run(dp.storage.close())
asyncio.run(dp.storage.wait_closed())
logger.info("Bot stopped polling")
