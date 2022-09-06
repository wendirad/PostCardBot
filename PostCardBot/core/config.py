"""Configuration file for the bot.

"""

from pathlib import Path

from decouple import Csv, config
from loguru import logger
from notifiers.logging import NotificationHandler

from PostCardBot.core.middlewares import (
    PostCardBotI18nMiddleware,
    UserMiddleware,
)

# Root directory of the project

ROOT_DIR = Path(__file__).resolve().parent.parent

# Bot token

API_TOKEN = config("API_TOKEN")

# Database

DATABASE_URL = config("DATABASE_URL")

DATABASE_NAME = config("DATABASE_NAME")

DATABASE_SELECTION_TIMEOUT = config(
    "DATABASE_SELECTION_TIMEOUT", cast=int, default=10 * 1000
)

STORAGE_DATABASE_NAME = config("STORAGE_DATABAES_NAME", default="aiogram_fsm")

# Logging

LOG_FILE_NAME = config("LOG_FILE_NAME", default="bot.log")

# Add debug logger

logger.add(
    ROOT_DIR.parent / "logs" / LOG_FILE_NAME,
    rotation=config("LOG_ROTATION_SIZE", default="100 MB"),
    backtrace=True,
    diagnose=True,
    level="DEBUG",
)

# Add notification logger for errors

logger.add(
    NotificationHandler(
        config("NOTIFIER"),
        defaults={
            "username": config("NOTIFIER_EMAIL"),
            "password": config("NOTIFIER_PASSWORD"),
            "to": config("NOTIFICATION_RECIPIENT"),
        },
    ),
    level="ERROR",
)

# Localization

LOCALE = config("LOCALE", default="en")

I18N_DOMAIN = "PostCardBot"

LOCALE_PATH = ROOT_DIR.parent / "locale"

LANGUAGES = (
    ("en", "🇺🇸 English"),
    ("am", "🇪🇹 አማርኛ"),
)

# Middlewares

i18n = PostCardBotI18nMiddleware(I18N_DOMAIN, LOCALE_PATH, default=LOCALE)

middlewares = [i18n, UserMiddleware()]
