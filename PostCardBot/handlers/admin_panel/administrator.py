"""Administrator handler for the bot."""

import enum

import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler, superuser_only
from PostCardBot.core.handlers import BaseHandler
from PostCardBot.core.model import User

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class AdministratorAddForm(StatesGroup):
    """Administrator add form."""

    id = State()


class AdministratorHandler(BaseHandler):
    """Administrator handler for the bot."""

    class Buttons(enum.Enum):
        """Administrator buttons."""

        BACK = _("🔙🔐 Admin panel")
        REMOVE = "❌ Remove"
        ADMINISTRATORS = _("👤 Administrators")
        ADD_ADMINISTRATOR = _("➕👤 Add Administrator")

    class Texts(enum.Enum):
        """Administrator texts."""

        NO_ADMIN = _("There are no administrator for this bot.")
        ADMIN_REMOVED = _("Admin {name} remove successfully.")
        ADMIN_NOT_FOUND = _("Admin not found.")
        ENTER_ID = _("Send user telegram id\n\ntype /cancel to cancel")
        ADMIN_ALREADY_EXISTS = _("{name} is already admin.")
        USER_NOT_FOUND = _("User with this id doesn't registerd on the bot.")
        INVALID_USER_ID = _(
            "Invalid telegram user id. Please try again with a"
            " valid telegram id. /cancel to cancel"
        )
        OPERAION_CANCELLED = _("Operation cancelled.")

    @staticmethod
    def get_user_detail(user):
        return _(
            "First name: {first_name}\n"
            "Last name: {last_name}\n"
            "Username: @{username}\n"
            "Joined: {created}\n"
        ).format(
            first_name=md.bold(user.first_name),
            last_name=md.bold(user.last_name or ""),
            username=md.bold(user.username or ""),
            created=md.bold(user.created.strftime("%c")),
        )

    @staticmethod
    def get_options():
        btn_cls = AdministratorHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.ADD_ADMINISTRATOR.value)),
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.BACK.value)),
        )
        return button_markup

    @Handler.message_handler(commands=["cancel"], state=[AdministratorAddForm])
    @superuser_only
    async def cancel_handler(message: types.Message, state):
        """Cancel handler."""

        await state.finish()
        await message.reply(
            AdministratorHandler.Texts.OPERATION_CANCELLED.value,
            reply_markup=AdministratorHandler.get_options(),
        )

    @Handler.message_handler(Text(equals=__(Buttons.ADMINISTRATORS.value)))
    @superuser_only
    async def administrators(message: types.Message):
        """Administrators command handler."""

        await message.answer(
            text=AdministratorHandler.Buttons.ADMINISTRATORS.value,
            reply_markup=AdministratorHandler.get_options(),
        )

        users = await User.filter(is_admin=True)

        if users:
            for user in users:
                inline_markup = types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            types.InlineKeyboardButton(
                                text=AdministratorHandler.Buttons.REMOVE.value,
                                callback_data="remove_admin:" + str(user.pk),
                            ),
                        ]
                    ]
                )
                await message.answer(
                    text=AdministratorHandler.get_user_detail(user),
                    reply_markup=inline_markup,
                    parse_mode=types.ParseMode.MARKDOWN,
                )
        else:
            await message.answer(
                text=AdministratorHandler.Texts.NO_ADMIN.value,
            )

    @Handler.callback_query_handler(Text(startswith="remove_admin:"))
    @superuser_only
    async def remove_admin(callback_query: types.CallbackQuery):
        """Remove user from admin."""

        admin_id = int(callback_query.data.split(":")[1])

        user = await User(id=admin_id, is_admin=True).get()

        if user:
            await User(id=user.id, is_admin=False).save()
            await callback_query.answer(
                text=AdministratorHandler.Texts.ADMIN_REMOVED.value.format(
                    name=user.first_name
                ),
            )
        else:
            await callback_query.answer(
                text=AdministratorHandler.Texts.ADMIN_NOT_FOUND.value,
            )
        await callback_query.message.edit_reply_markup(reply_markup=None)

    @Handler.message_handler(Text(equals=__(Buttons.ADD_ADMINISTRATOR.value)))
    @superuser_only
    async def add_administrator(message: types.Message):
        """Add administrator."""

        await AdministratorAddForm.first()
        await message.answer(
            AdministratorHandler.Texts.ENTER_ID.value,
            reply_markup=types.ReplyKeyboardRemove(),
        )

    @Handler.message_handler(
        content_types=types.ContentType.TEXT, state=AdministratorAddForm.id
    )
    @superuser_only
    async def process_admin_id(message, state):
        """Set user as admin if exists."""

        user_id = message.text

        if not user_id.isdigit():
            await message.answer(
                text=AdministratorHandler.Texts.INVALID_USER_ID.value,
            )
            return
        else:
            user_id = int(user_id)

        user = await User(id=user_id).get()

        if user:
            if user.is_admin:
                await message.answer(
                    text=(
                        AdministratorHandler.Texts.ADMIN_ALREADY_EXISTS.value.format(  # noqa: E501
                            name=md.bold(user.first_name)
                        )
                    ),
                    reply_markup=AdministratorHandler.get_options(),
                    parse_mode=types.ParseMode.MARKDOWN,
                )
            else:
                await User(id=user.id, is_admin=True).save()
                await message.answer(
                    text="NEW ADMIN\n\n"
                    + AdministratorHandler.get_user_detail(user),
                    reply_markup=AdministratorHandler.get_options(),
                    parse_mode=types.ParseMode.MARKDOWN,
                )
        else:
            await message.answer(
                text=AdministratorHandler.Texts.USER_NOT_FOUND.value,
                reply_markup=AdministratorHandler.get_options(),
                parse_mode=types.ParseMode.MARKDOWN,
            )
        await state.finish()
