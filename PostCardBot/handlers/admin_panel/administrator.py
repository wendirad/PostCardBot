"""Administrator handler for the bot."""

import enum

from aiogram import types
from aiogram.dispatcher.filters import Text

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler, superuser_only
from PostCardBot.core.handlers import BaseHandler

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class AdministratorHandler(BaseHandler):
    """Administrator handler for the bot."""

    class Buttons(enum.Enum):
        """Administrator buttons."""

        BACK = _("🔙🔐 Admin panel")
        ADMINISTRATORS = _("👤 Administrators")

    @Handler.message_handler(Text(equals=__(Buttons.ADMINISTRATORS.value)))
    @superuser_only
    async def administrators(message: types.Message):
        """Administrators command handler."""

        btn_cls = AdministratorHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.BACK.value)),
        )
        await message.answer(
            text=_("Administrators"), reply_markup=button_markup
        )
