"""Utils for PostCardBot."""

from aiogram import Dispatcher


def load_handlers(bot, dp):
    """Load all handlers from the handlers directory."""

    Dispatcher.set_current(dp)

    from PostCardBot.handlers import __all__ as handlers

    for handler in handlers:
        handler.register(bot, dp)
