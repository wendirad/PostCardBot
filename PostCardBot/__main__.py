"""PostCardBot - Telegram bot for sending postcards."""

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from loguru import logger

from PostCardBot.core import config
from PostCardBot.core.utils import load_handlers

# Setup the storage for states
storage = MemoryStorage()

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot, storage=storage)

# Setup the middleware
for middleware in config.middlewares:
    dp.middleware.setup(middleware)

# Register handlers
load_handlers(bot, dp)

logger.info("Bot start polling")
executor.start_polling(dp, skip_updates=True)
logger.info("Bot stopped polling")
