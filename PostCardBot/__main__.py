"""PostCardBot - Telegram bot for sending postcards."""

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from loguru import logger

from PostCardBot.core import config

# Setup the storage for states
storage = MemoryStorage()

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=storage)

logger.info("Bot start polling")
executor.start_polling(dp, skip_updates=True)
logger.info("Bot stopped polling")