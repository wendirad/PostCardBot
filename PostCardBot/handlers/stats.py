"""Stats handler."""

import enum
import io

from aiogram import types
from aiogram.dispatcher.filters import Text

import matplotlib.pyplot as plt

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler, admin_only, superuser_only
from PostCardBot.core.handlers import BaseHandler
from PostCardBot.models import User

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class StatsHandler(BaseHandler):
    """Stats handler."""

    class Buttons(enum.Enum):
        """Stats buttons."""

        USERS = _("👥📈 Users")
        ADMINISTRATORS = _("👤📈 Administrators")
        POSTCARDS = _("📦📈 Postcards")
        STATS = _("📊 Stats")
        BACK = _("🔙🔐 Admin panel")

    @Handler.message_handler(Text(equals=__(Buttons.STATS.value)))
    @admin_only
    async def stats(message: types.Message):
        """Stats command handler."""

        btn_cls = StatsHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(types.KeyboardButton(__(btn_cls.POSTCARDS.value)))
        button_markup.add(types.KeyboardButton(__(btn_cls.USERS.value)))
        if message.from_user.is_superuser:
            button_markup.add(
                types.KeyboardButton(__(btn_cls.ADMINISTRATORS.value))
            )
        button_markup.add(types.KeyboardButton(__(btn_cls.BACK.value)))
        await message.answer(text=_("Stats"), reply_markup=button_markup)

    @Handler.message_handler(Text(equals=__(Buttons.USERS.value)))
    @admin_only
    async def users(message: types.Message):
        """Users command handler."""

        total_user = await User.count()
        # Aggregate users by date
        users = await User.all()
        users_by_date = {}
        for user in users:
            created = user.created.strftime("%Y-%m-%d")
            if created not in users_by_date:
                users_by_date[created] = 1
            else:
                users_by_date[created] += 1

        stats = _("Total users: {}").format(total_user)
        bio = io.BytesIO()
        plt.plot(
            users_by_date.keys(),
            users_by_date.values(),
            color="red",
            linewidth=2,
            linestyle="-",
            marker="o",
        )
        plt.title(_("Users by date"))
        plt.ylabel(_("Users"))
        plt.xlabel(_("Date"))
        plt.tight_layout()
        plt.savefig(bio, format="png")
        bio.seek(0)
        await message.answer_photo(bio, caption=stats)

    @Handler.message_handler(Text(equals=__(Buttons.ADMINISTRATORS.value)))
    @superuser_only
    async def admins(message: types.Message):
        """Admins command handler."""

        await message.answer(text=_("Admins"))

    @Handler.message_handler(Text(equals=__(Buttons.POSTCARDS.value)))
    @admin_only
    async def postcards(message: types.Message):
        """Postcards command handler."""

        await message.answer(text=_("Postcards"))
