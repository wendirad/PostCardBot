# flake8: noqa: W605
"""Main menu handler."""

import enum

import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher.filters import Text

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler, admin_only
from PostCardBot.core.handlers import BaseHandler
# from PostCardBot.handlers.admin_panel import AdminPanelHandler
from PostCardBot.handlers.settings import SettingsHandler

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class MainMenuHandler(BaseHandler):  # noqa: N801
    """Main menu handler."""

    class Buttons(enum.Enum):
        """Main menu buttons."""

        # Main menu
        SEND_POSTCARD = _("📬 Send postcard")
        MY_POSTCARDS = _("📎 My postcards")
        HELP = _("💡 Help")
        ABOUT = _("📖 About")
        ADMIN_PANEL = _("🔐 Admin panel")

        # Admin panel
        POSTCARDS = _("📦 Postcards")
        USERS = _("👥 Users")
        STATS = _("📊 Stats")
        ADMINISTRATORS = _("👤 Administrators")

        # Back buttons
        BACK_MAIN_MENU = _("🔙🏠 Main menu")
        BACK_ADMIN_PANEL = _("🔙🔐 Admin panel")

    @Handler.message_handler(commands=["start"])
    async def start(message: types.Message, is_back=False):
        """Start command handler."""

        bot = await message.bot.get_me()
        welcome_text = _(
            "👋 Hello `{first_name}`\n\nWelcome to ✉️📮 \- {bot_name}\! \- 📬🏠\."
            "\n{bot_link} is a Telegram bot, that provided simple and fun "
            "postcard serivce for user\. Select postcard and share with your "
            "friends Easy\. right? 😉\n\n"
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

        btn_cls = MainMenuHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(_(btn_cls.SEND_POSTCARD.value)),
            types.KeyboardButton(_(btn_cls.MY_POSTCARDS.value)),
        )
        button_markup.add(
            types.KeyboardButton(_(SettingsHandler.Buttons.SETTINGS.value)),
        )
        if message.from_user.is_superuser or message.from_user.is_admin:
            button_markup.add(
                types.KeyboardButton(_(btn_cls.ADMIN_PANEL.value)),
            )
        button_markup.add(
            types.KeyboardButton(_(btn_cls.HELP.value)),
            types.KeyboardButton(_(btn_cls.ABOUT.value)),
        )
        await message.answer(
            text=welcome_text if not is_back else _("🏠 Main menu"),
            reply_markup=button_markup,
            parse_mode="MarkdownV2",
        )

    @Handler.message_handler(Text(equals=__(Buttons.BACK_MAIN_MENU.value)))
    async def back(message: types.Message):
        """Back command handler."""

        await MainMenuHandler.start(message, is_back=True)

    @Handler.message_handler(Text(equals=__(Buttons.BACK_ADMIN_PANEL.value)))
    @Handler.message_handler(Text(equals=__(Buttons.ADMIN_PANEL.value)))
    @admin_only
    async def admin_panel(message: types.Message):
        """Admin panel command handler."""

        btn_cls = MainMenuHandler.Buttons
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
            types.KeyboardButton(__(btn_cls.BACK_MAIN_MENU.value)),
        )
        await message.answer(
            text=_("🔐 Admin panel"), reply_markup=button_markup
        )

    @Handler.message_handler(Text(equals=__(Buttons.ABOUT.value)))
    async def about(message: types.Message):
        """About command handler."""

        about_message = _(
            "🅰️🅱️🅾️⛎➕\n\n"
            "At Backos Technologies we believe that we can bring the greatness"
            " that our country had in the past by solving social, economic and"
            " political problems using modern technologies\.\n\n"
            "This bot is developed by {organazation_link} and is licensed"
            "under the {license_link} license\.\n\n"
        ).format(
            organazation_link=md.link(
                _("Backos Technologies"), "https://www.backostech.com"
            ),
            license_link=md.link(
                _("Apache License 2.0"),
                "https://www.apache.org/licenses/LICENSE-2.0",
            ),
        )
        await message.answer(text=about_message, parse_mode="MarkdownV2")

    @Handler.message_handler(Text(equals=__(Buttons.HELP.value)))
    async def help(message: types.Message):
        """Help command handler."""

        help_message = _(
            "♓️3⃣🕒🅿️\n\n"
            "*Send postcard*\n"
            "Send postcard to your friends\.\n\n"
            "*My postcards*\n"
            "Check your postcards\.\n\n"
            "*Settings*\n"
            "Change settings\.\n\n"
            "*Help*\n"
            "Check available options\.\n\n"
            "*About*\n"
            "Check bot information\."
        )

        if message.from_user.is_superuser or message.from_user.is_admin:
            help_message += _("\n\n*Admin panel*\n" "Access admin panel\.\n\n")

        await message.answer(text=help_message, parse_mode="MarkdownV2")
