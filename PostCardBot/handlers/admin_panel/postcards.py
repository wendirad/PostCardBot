"""Admin panel handler."""

import enum

from aiogram import types
from aiogram.dispatcher.filters import Text

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler, admin_only
from PostCardBot.core.handlers import BaseHandler

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class AdminPanelPostCardsHandler(BaseHandler):
    """Admin panel handler."""

    class Buttons(enum.Enum):
        """Admin panel buttons."""

        POSTCARDS = _("📦 Postcards")
        BACK = _("🔙🔐 Admin panel")

    @Handler.message_handler(Text(equals=__(Buttons.POSTCARDS.value)))
    @admin_only
    async def postcards(message: types.Message):
        """Postcards command handler."""

        btn_cls = AdminPanelPostCardsHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.BACK.value)),
        )
        await message.answer(text=_("Postcards"), reply_markup=button_markup)
