"""User postcards handler."""

import enum

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery

from bson import ObjectId
from loguru import logger

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler
from PostCardBot.core.handlers import BaseHandler
from PostCardBot.core.helpers import create_postcard
from PostCardBot.models import Category, PostCard
from PostCardBot.handlers.main_menu import MainMenuHandler

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class SendPostCard(StatesGroup):
    """Send postcard state."""

    from_user = State()
    to_user = State()
    confirm = State()


class UserPostCardHandler(BaseHandler):
    """Settings handler."""

    class Buttons(enum.Enum):
        """Settings buttons."""

        BACK = _("🔙🏠 Main menu")
        SEND = _("📬 Use this template")
        SHARE = _("📤 Share")

        SEND_POSTCARD = _("📬 Send postcard")

        CATEGORY_NOT_FOUND = _("📁 Category not found")
        POSTCARDS_NOT_FOUND = _("📎 Postcards not found")

        CONFRIM = _("✅ Confirm")
        CANCEL = _("❌ Cancel")

    class Texts(enum.Enum):
        """User postcard texts."""

        SELECT_CATEGORY = _("Select category")
        SELECT_POSTCARD_TEMPLATE = _("Select postcard template")

        ENTER_SENDER_NAME = _("Enter sender name")
        ENTER_RECEIVER_NAME = _("Enter receiver name")

        CONFIRM_SEND_POSTCARD = ("Send this postcard?")
        POSTCARD_CAPTION = _("Postcard from")
        POSTCARD_SEND_CANCELED = _("Postcard send canceled")

    @Handler.message_handler(Text(equals=__(Buttons.SEND_POSTCARD.value)))
    async def send_postcard_handler(message: types.Message):
        """Settings command handler."""

        # Load categories
        categories = await Category.filter(is_active=True)
        inline_markup = types.InlineKeyboardMarkup()
        for category in categories:
            inline_markup.row(
                types.InlineKeyboardButton(
                    category.name,
                    callback_data=f"category:{category.pk}",
                )
            )
        await message.answer(
            text=__(UserPostCardHandler.Texts.SELECT_CATEGORY.value),
            reply_markup=inline_markup,
        )

    @Handler.callback_query_handler(Text(startswith="category:"))
    async def category_handler(call: CallbackQuery, state: FSMContext):
        """Category handler."""

        category_id = ObjectId(call.data.split(":")[1])
        category = await Category(_id=category_id).get()

        if category and category.is_active:
            postcards = await PostCard.filter(
                category_id=category_id, is_active=True
            )
            bot = Bot.get_current()
            await bot.send_message(
                chat_id=call.from_user.id,
                text=__(
                    UserPostCardHandler.Texts.SELECT_POSTCARD_TEMPLATE.value
                ),
            )
            if postcards:
                for postcard in postcards:
                    await bot.send_photo(
                        chat_id=call.from_user.id,
                        photo=postcard.thumbnail,
                        caption=postcard.name + "\n\n" + postcard.description,
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton(
                                UserPostCardHandler.Buttons.SEND.value,
                                callback_data=f"send_postcard:{postcard.pk}",
                            )
                        ),
                    )
            else:
                await bot.send_message(
                    chat_id=call.from_user.id,
                    text=__(
                        UserPostCardHandler.Buttons.POSTCARDS_NOT_FOUND.value
                    ),
                )
        else:
            await call.message.answer(
                UserPostCardHandler.Buttons.CATEGORY_NOT_FOUND.value
            )

    @Handler.callback_query_handler(Text(startswith="send_postcard:"))
    async def send_postcard_handler(call: CallbackQuery, state: FSMContext):
        """Send postcard handler."""

        postcard_id = ObjectId(call.data.split(":")[1])
        postcard = await PostCard(_id=postcard_id).get()
        if postcard and postcard.is_active:
            dp = Dispatcher.get_current()
            state = dp.current_state()
            async with state.proxy() as data:
                data["postcard"] = postcard

            await SendPostCard.from_user.set()
            await call.message.answer(
                text=UserPostCardHandler.Texts.ENTER_SENDER_NAME.value,
                reply_markup=types.ReplyKeyboardRemove(),
                parse_mode=types.ParseMode.MARKDOWN,
            )
        else:
            await call.message.answer(
                UserPostCardHandler.Buttons.POSTCARDS_NOT_FOUND.value
            )

    @Handler.message_handler(
        content_types=types.ContentType.TEXT, state=SendPostCard.from_user
    )
    async def process_from_user(message: types.Message, state: FSMContext):
        """Process from user."""

        async with state.proxy() as data:
            data["from_user"] = message.text
        await SendPostCard.next()
        await message.answer(UserPostCardHandler.Texts.ENTER_RECEIVER_NAME.value)

    @Handler.message_handler(
        content_types=types.ContentType.TEXT, state=SendPostCard.to_user
    )
    async def process_to_user(message: types.Message, state: FSMContext):
        """Process to user."""

        async with state.proxy() as data:
            data["to_user"] = message.text

            await SendPostCard.next()
            await message.answer_chat_action("upload_photo")

            new_postcard = await create_postcard(
                data["postcard"].image, data["from_user"], data["to_user"]
            )


            prepared_message = await message.answer_photo(
                photo=new_postcard,
                caption=UserPostCardHandler.Texts.CONFIRM_SEND_POSTCARD.value,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton(
                        UserPostCardHandler.Buttons.CONFRIM.value,
                        callback_data="confirm_send_postcard",
                    ),
                    types.InlineKeyboardButton(
                        UserPostCardHandler.Buttons.CANCEL.value,
                        callback_data="cancel_send_postcard",
                    ),
                ),
            )
            data["message_id"] = prepared_message.message_id

    @Handler.callback_query_handler(
        Text(startswith="confirm_send_postcard"),
        state=SendPostCard.confirm,
    )
    async def confirm_send_postcard_handler(
        call: CallbackQuery, state: FSMContext
    ):
        """Confirm send postcard handler."""


        async with state.proxy() as data:
            await call.message.edit_caption(
                caption=UserPostCardHandler.Texts.POSTCARD_CAPTION.value,
                reply_markup=None,
            )
            call.answer()
            await state.finish()

            logger.info(
                f"Postcard sent from {data['from_user']} to {data['to_user']}"
                f"Using template {data['postcard'].name}({data['postcard'].pk})"
            )

            await MainMenuHandler.start(call.message, is_back=True)

    @Handler.callback_query_handler(
        Text(startswith="cancel_send_postcard"),
        state=SendPostCard.confirm,
    )
    async def cancel_send_postcard_handler(
        call: CallbackQuery, state: FSMContext
    ):
        """Cancel send postcard handler."""

        # await call.message.delete()
        # await state.finish()

        await Bot.get_current().send_message(
            chat_id=call.from_user.id,
            text=__(UserPostCardHandler.Texts.POSTCARD_SEND_CANCELED.value),
            reply_markup=types.ReplyKeyboardRemove(),
        )

        dp = Dispatcher.get_current()

        await dp.process_update(
            types.Update(
                update_id=call.message.message_id,
                message=types.Message(
                    message_id=call.message.message_id,
                    chat=types.Chat(
                        id=call.from_user.id,
                        type=call.chat_instance,
                        username=call.from_user.username,
                    ),
                    text="/start",
                    kwargs={"is_back": True},
                ),
            )
        )


