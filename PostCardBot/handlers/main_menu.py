# flake8: noqa

"""Main menu handler."""

import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher.filters import Text

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler
from PostCardBot.core.handlers import BaseHandler
from PostCardBot.models import User

_ = config.i18n.gettext


class MainMenuHandler(BaseHandler):
    """Main menu handler."""

    @Handler.message_handler(commands=["start"])
    async def start(message: types.Message):
        """Start command handler."""
        bot = await message.bot.get_me()

        welcome_text = _(
            "👋 Hello `{first_name}`\n\nWelcome to ✉️📮 \- {bot_name}\! \- 📬🏠\."
            "\n{bot_link} is a Telegram bot, that provided simple and fun "
            "postcard serivce for user\. Select postcard and share with your "
            "friedns Easy\. right? 😉\n\n"
            "If you are new, press `Help` to check available options\."
            "Brought To You By: {organazation_link}"
        ).format(
            first_name=message.from_user.first_name,
            bot_name=md.bold(bot.first_name),
            bot_link=md.link(bot.first_name, bot.url),
            organazation_link=md.link(
                _("Backos Technologies"), "https://www.backostech.com"
            ),
        )

        markup = types.InlineKeyboardMarkup(resize_keyboard=True)
        for lang_code, lang_name in config.LANGUAGES:
            markup.add(
                types.InlineKeyboardButton(
                    text=lang_name,
                    callback_data=f"change_language:{lang_code}",
                )
            )
        await message.answer(
            text=welcome_text,
            reply_markup=markup,
        )

    @Handler.callback_query_handler(Text(startswith="change_language"))
    async def change_language(callback_query: types.CallbackQuery):
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
