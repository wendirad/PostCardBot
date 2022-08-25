"""Utils for PostCardBot."""

from aiogram import Dispatcher


def load_handlers(bot, dp):
    """Load all handlers from the handlers directory."""

    Dispatcher.set_current(dp)

    import PostCardBot.handlers  # noqa: F401
