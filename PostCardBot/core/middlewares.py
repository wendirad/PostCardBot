"""Middleware for the PostCardBot."""

from typing import Any, Optional, Tuple

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

class PostCardBotI18nMiddleware(I18nMiddleware):
    """Middleware for the PostCardBot."""

    async def get_user_locale(
        self, action: str, args: Tuple[Any]
    ) -> Optional[str]:
        from PostCardBot.core.model import User

        current_user = types.User.get_current()
        if current_user is not None:
            user = await User(id=current_user.id).get_or_create()
            locale = user.locale if user else None
            if locale and locale.language in self.locales:
                *_, data = args
                language = data["locale"] = locale.language
                return language
        return self.default


class UserMiddleware(LifetimeControllerMiddleware):
    """Middleware for the PostCardBot User."""

    async def pre_process(self, obj, data, *args):
        """Update user while user interacts with the bot."""

        from PostCardBot.core.model import User

        if isinstance(obj, (types.Message, types.CallbackQuery)):
            current_user = types.User.get_current()
            if current_user is not None:
                user = await User(
                    **current_user.to_python(), is_active=True
                ).save()
                current_user.is_admin = user.is_admin
                current_user.is_superuser = user.is_superuser
                current_user.is_active = user.is_active
            return True
