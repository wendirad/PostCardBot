"""Handler functions for the bot."""

from aiogram import Bot, Dispatcher


class BaseHandler:
    """Handler class for the bot.

    Used to attach bot and dispatcher into the class.
    """

    @classmethod
    def register(cls, bot: Bot, dp: Dispatcher) -> None:
        """
        Register the handler.
        """
        cls.dp = dp
        cls.bot = bot
