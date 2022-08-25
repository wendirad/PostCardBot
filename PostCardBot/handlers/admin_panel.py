"""Admin panel handler."""

import enum

from aiogram import types
from aiogram.dispatcher.filters import Text

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler, admin_only
from PostCardBot.core.handlers import BaseHandler

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class AdminPanelHandler(BaseHandler):
    """Admin panel handler."""

    class Buttons(enum.Enum):
        """Admin panel buttons."""

        ADMIN_PANEL = _("🔐 Admin panel")
        POSTCARDS = _("📦 Postcards")
        USERS = _("👥 Users")
        STATS = _("📊 Stats")
        ADMINISTRATORS = _("👤 Administrators")
        MAIN_MENU = _("🔙🏠 Main menu")
        BACK = _("🔙🔐 Admin panel")

    @Handler.message_handler(Text(equals=__(Buttons.BACK.value)))
    @admin_only
    async def back(message: types.Message):
        """Back command handler."""

        await AdminPanelHandler.admin_panel(message)

    @Handler.message_handler(Text(equals=__(Buttons.ADMIN_PANEL.value)))
    @admin_only
    async def admin_panel(message: types.Message):
        """Admin panel command handler."""

        btn_cls = AdminPanelHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.POSTCARDS.value)),
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.USERS.value)),
            types.KeyboardButton(__(btn_cls.STATS.value)),
        )
        if message.from_user.is_superuser:
            button_markup.add(
                types.KeyboardButton(__(btn_cls.ADMINISTRATORS.value)),
            )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.MAIN_MENU.value)),
        )
        await message.answer(
            text=_("🔐 Admin panel"), reply_markup=button_markup
        )

    @Handler.message_handler(Text(equals=__(Buttons.USERS.value)))
    @admin_only
    async def users(message: types.Message):
        """Users command handler."""

        btn_cls = AdminPanelHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.BACK.value)),
        )
        await message.answer(text=_("Users"), reply_markup=button_markup)

    @Handler.message_handler(Text(equals=__(Buttons.POSTCARDS.value)))
    @admin_only
    async def postcards(message: types.Message):
        """Postcards command handler."""

        btn_cls = AdminPanelHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.BACK.value)),
        )
        await message.answer(text=_("Postcards"), reply_markup=button_markup)
