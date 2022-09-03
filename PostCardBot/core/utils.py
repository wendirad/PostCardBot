"""Utils for PostCardBot."""

from aiogram import Bot, Dispatcher


def load_handlers(bot, dp):
    """Load all handlers from the handlers directory."""

    Dispatcher.set_current(dp)
    Bot.set_current(bot)

    import PostCardBot.handlers  # noqa: F401
