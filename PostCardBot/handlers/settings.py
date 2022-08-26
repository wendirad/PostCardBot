"""Setting button handler."""

import enum

from aiogram import types
from aiogram.dispatcher.filters import Text

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler
from PostCardBot.core.handlers import BaseHandler
from PostCardBot.core.model import User

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class SettingsHandler(BaseHandler):
    """Settings handler."""

    class Buttons(enum.Enum):
        """Settings buttons."""

        BACK = _("🔙🏠 Main menu")
        SETTINGS = _("⚙️ Settings")
        CHANGE_LANGUAGE = _("🌐 Change language")

    @Handler.message_handler(Text(equals=__(Buttons.SETTINGS.value)))
    async def settings(message: types.Message):
        """Settings command handler."""

        btn_cls = SettingsHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.CHANGE_LANGUAGE.value)),
        )
        button_markup.add(
            types.KeyboardButton(_(btn_cls.BACK.value)),
        )
        await message.answer(text=_("Settings"), reply_markup=button_markup)

    @Handler.message_handler(Text(equals=__(Buttons.CHANGE_LANGUAGE.value)))
    async def change_language(message: types.Message):
        """Change language handler."""

        inline_markup = types.InlineKeyboardMarkup(resize_keyboard=True)
        for lang_code, lang_name in config.LANGUAGES:
            inline_markup.add(
                types.InlineKeyboardButton(
                    text=lang_name,
                    callback_data=f"change_language:{lang_code}",
                )
            )

        await message.answer(
            text=_("Select language"),
            reply_markup=inline_markup,
        )

    @Handler.callback_query_handler(Text(startswith="change_language"))
    async def set_language(callback_query: types.CallbackQuery):
        """Change language handler."""

        await User(
            id=callback_query.from_user.id,
            selected_language=callback_query.data.split(":")[1],
        ).save()
        await callback_query.answer()
        await callback_query.message.edit_reply_markup(reply_markup=None)
        await callback_query.message.answer(
            text=_("Your language preference has been changed.")
        )
