"""Middleware for the PostCardBot."""

from typing import Any, Optional, Tuple

from aiogram import types
from aiogram.contrib.middlewares.i18n import BaseMiddleware, I18nMiddleware


class PostCardBotI18nMiddleware(I18nMiddleware):
    """Middleware for the PostCardBot."""

    async def get_user_locale(
        self, action: str, args: Tuple[Any]
    ) -> Optional[str]:
        from PostCardBot.models.user import User

        current_user = types.User.get_current()
        if current_user is not None:
            user = await User(id=current_user.id).get()
            locale = user.locale if user else None
            if locale and locale.language in self.locales:
                *_, data = args
                language = data["locale"] = locale.language
                return language
        return self.default


class UserMiddleware(BaseMiddleware):
    """Middleware for the PostCardBot User."""

    async def trigger(self, action: str, args: Tuple[Any]) -> None:
        """
        Update user while user interacts with the bot.

        :param action:
        :param args:
        :return:
        """
        from PostCardBot.models.user import User

        current_user = types.User.get_current()
        if current_user is not None:
            await User(**current_user.to_python()).save()
        return True
