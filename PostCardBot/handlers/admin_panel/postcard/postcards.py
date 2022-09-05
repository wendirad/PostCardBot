"""Admin panel handler."""

import enum
from io import BytesIO

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bson import ObjectId
from loguru import logger
from PIL import Image

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler, admin_only
from PostCardBot.core.handlers import BaseHandler
from PostCardBot.models import Category, PostCard

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class PostCardAddForm(StatesGroup):
    """PostCard add form."""

    name = State()
    description = State()
    image = State()


class PostCardEditForm(StatesGroup):
    """PostCard edit form."""

    name = State()
    description = State()
    image = State()


class AdminPanelPostCardsHandler(BaseHandler):
    """Admin panel handler."""

    class Buttons(enum.Enum):
        """Admin panel buttons."""

        POSTCARDS = _("📦 Postcards")
        ADD_POSTCARD = _("➕📦 Add postcard")
        EDIT = "📝 Edit"
        DELETE = "🗑 Delete"
        YES = "✅ Yes, delete"
        NO = "❌ No, cancel"
        ACTIVATE = "✅ Activate"
        DEACTIVATE = "❌ Deactivate"
        BACK = _("🔙📁 Back to categories")

    class Texts(enum.Enum):
        """Admin panel texts."""

        ALL_POSTCARDS = _("Here are all postcards in category {name}")
        NO_POSTCARDS = _("There are no postcards in category {name}")
        NO_CATEGORY_SELECTED = _(
            "No category selected. Please select category first"
        )

        ENTER_POSTCARD_NAME = _("Enter postcard name")
        ENTER_POSTCARD_DESCRIPTION = _("Enter postcard description")
        ENTER_POSTCARD_IMAGE = _("Send postcard image")
        POSTCARD_ADDED = _("Postcard added successfully.")

        EDIT_NAME = _(
            "{name}\n\nEnter new postcard name\n\ntype "
            "/cancel to cancel /skip to skip changing name."
        )
        EDIT_DESCRIPTION = _(
            "{description}\n\nEnter new postcard description\n\n type "
            "/cancel to cancel or /skip to skip changing description."
        )
        EDIT_IMAGE = _(
            "Send new postcard image\n\n type /cancel to cancel or"
            " /skip to skip changing image."
        )
        POSTCARD_EDITED = _("Postcard edited successfully.")

        OPERATION_CANCELLED = _("Operation cancelled.")

        CONFIRM_DELETE = _("Are you sure you want to delete postcard {name}?")
        POSTCARD_DELETED = _("Postcard {name} deleted successfully.")

    @staticmethod
    def get_options(postcard):
        btn_cls = AdminPanelPostCardsHandler.Buttons
        return types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=btn_cls.EDIT.value,
                        callback_data="edit_postcard:" + str(postcard.pk),
                    ),
                    types.InlineKeyboardButton(
                        text=btn_cls.DELETE.value,
                        callback_data="delete_postcard:" + str(postcard.pk),
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        text=btn_cls.DEACTIVATE.value
                        if postcard.is_active
                        else btn_cls.ACTIVATE.value,
                        callback_data="change_postcard_status:"
                        + str(postcard.pk),
                    )
                ],
            ]
        )

    @staticmethod
    async def save_updated_data(message, state):
        async with state.proxy() as data:
            if message.text != "/skip":
                data["image"] = message.photo[-1].file_id
                image_byte = BytesIO()
                out_image = BytesIO()
                await message.photo[-1].download(destination_file=image_byte)

                image = Image.open(image_byte)
                image.thumbnail((300, 300))
                image.save(out_image, format="PNG")
                out_image.seek(0)

                bot = Bot.get_current()

                thumbnail_message = await bot.send_photo(
                    chat_id=message.chat.id,
                    photo=out_image,
                )
                data["thumbnail"] = thumbnail_message.photo[-1].file_id
                await bot.delete_message(
                    chat_id=thumbnail_message.chat.id,
                    message_id=thumbnail_message.message_id,
                )
            old_postcard = data.pop("postcard", None)
            for key, value in old_postcard.to_dict().items():
                data.setdefault(key, value)

            postcard = await PostCard(**data).save()

            await Bot.get_current().send_photo(
                chat_id=message.chat.id,
                photo=postcard.thumbnail,
                caption=postcard.name + "\n\n" + postcard.description,
                reply_markup=AdminPanelPostCardsHandler.get_options(postcard),
                parse_mode=types.ParseMode.MARKDOWN,
            )

    @Handler.message_handler(
        commands=["cancel"], state=[PostCardAddForm, PostCardEditForm]
    )
    @admin_only
    async def cancel_handler(self, message: types.Message, state: FSMContext):
        """Cancel handler."""

        await state.finish()
        await message.reply(
            AdminPanelPostCardsHandler.Texts.OPERATION_CANCELLED.value,
            reply=False,
        )

    @Handler.message_handler(commands=["skip"], state=[PostCardEditForm.name])
    async def skip_name_edit(message: types.Message, state: FSMContext):
        """Skip name edit."""
        async with state.proxy() as data:
            await message.answer(
                AdminPanelPostCardsHandler.Texts.EDIT_DESCRIPTION.value.format(
                    description=data["postcard"].description
                ),
                parse_mode=types.ParseMode.MARKDOWN,
            )

        await PostCardEditForm.next()

    @Handler.message_handler(
        commands=["skip"], state=[PostCardEditForm.description]
    )
    @admin_only
    async def skip_description_edit(message: types.Message, state: FSMContext):
        """Skip description edit."""

        await PostCardEditForm.next()
        async with state.proxy() as data:
            await message.answer_photo(
                data["postcard"].thumbnail,
                caption=AdminPanelPostCardsHandler.Texts.EDIT_IMAGE.value,
                parse_mode=types.ParseMode.MARKDOWN,
            )

    @Handler.message_handler(commands=["skip"], state=[PostCardEditForm.image])
    @admin_only
    async def skip_image_edit(message: types.Message, state: FSMContext):
        """Skip image edit."""

        await AdminPanelPostCardsHandler.save_updated_data(message, state)

        await state.finish()

        btn_cls = AdminPanelPostCardsHandler.Buttons

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        markup.add(types.KeyboardButton(text=btn_cls.ADD_POSTCARD.value))
        markup.add(types.KeyboardButton(text=btn_cls.BACK.value))

        await message.answer(
            AdminPanelPostCardsHandler.Texts.POSTCARD_EDITED.value,
            reply_markup=markup,
        )

        logger.info("Postcard edited successfully.")

    @Handler.callback_query_handler(Text(startswith="postcards:"))
    @admin_only
    async def postcards(callback_query: types.CallbackQuery):
        """Show categorical postcards."""

        category = await Category(
            _id=ObjectId(callback_query.data.split(":")[1])
        ).get()

        postcards = await PostCard.filter(
            category_id=ObjectId(callback_query.data.split(":")[1])
        )

        bot = Bot.get_current()

        btn_cls = AdminPanelPostCardsHandler.Buttons

        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        markup.add(types.KeyboardButton(text=btn_cls.ADD_POSTCARD.value))
        markup.add(types.KeyboardButton(text=btn_cls.BACK.value))

        if postcards:
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text=(
                    AdminPanelPostCardsHandler.Texts.ALL_POSTCARDS.value.format(  # noqa: E501
                        name=md.bold(category.name)
                    )
                ),
                reply_markup=markup,
                parse_mode=types.ParseMode.MARKDOWN,
            )
            for postcard in postcards:
                await bot.send_photo(
                    chat_id=callback_query.message.chat.id,
                    photo=postcard.thumbnail,
                    caption=postcard.name + "\n\n" + postcard.description,
                    reply_markup=AdminPanelPostCardsHandler.get_options(
                        postcard
                    ),
                    parse_mode=types.ParseMode.MARKDOWN,
                )
            logger.info(
                "Showing categorical postcards for category %s"
                % callback_query.data.split(":")[1]
            )
        else:
            await bot.send_message(
                text=(
                    AdminPanelPostCardsHandler.Texts.NO_POSTCARDS.value.format(
                        name=category.name
                    )
                ),
                chat_id=callback_query.message.chat.id,
                reply_markup=markup,
                parse_mode=types.ParseMode.MARKDOWN,
            )

        dp = Dispatcher.get_current()
        state = dp.current_state()

        async with state.proxy() as data:
            data["category"] = category

    @Handler.message_handler(Text(equals=__(Buttons.ADD_POSTCARD.value)))
    @admin_only
    async def add_postcard(message: types.Message):
        """Add postcard."""

        current_state = Dispatcher.get_current().current_state()
        async with current_state.proxy() as data:
            category = data.get("category")
            if not category:
                await message.answer(
                    AdminPanelPostCardsHandler.Texts.NO_CATEGORY_SELECTED.value,  # noqa E501
                    parse_mode=types.ParseMode.MARKDOWN,
                )
                return
        await PostCardAddForm.name.set()

        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data["category_id"] = category.pk

        await message.answer(
            AdminPanelPostCardsHandler.Texts.ENTER_POSTCARD_NAME.value,
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(state=PostCardAddForm.name)
    @admin_only
    async def process_postcard_name(message: types.Message, state: FSMContext):
        """Postcard name."""

        async with state.proxy() as data:
            data["name"] = message.text

        await PostCardAddForm.description.set()
        await message.answer(
            AdminPanelPostCardsHandler.Texts.ENTER_POSTCARD_DESCRIPTION.value,
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(state=PostCardAddForm.description)
    @admin_only
    async def process_postcard_description(
        message: types.Message, state: FSMContext
    ):
        """Postcard description."""

        async with state.proxy() as data:
            data["description"] = message.text

        await PostCardAddForm.image.set()
        await message.answer(
            AdminPanelPostCardsHandler.Texts.ENTER_POSTCARD_IMAGE.value,
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(
        content_types=types.ContentType.PHOTO, state=PostCardAddForm.image
    )
    @admin_only
    async def process_postcard_image(
        message: types.Message, state: FSMContext
    ):
        """Postcard image."""

        postcard = await AdminPanelPostCardsHandler.save_updated_data(
            message, state
        )

        btn_cls = AdminPanelPostCardsHandler.Buttons
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        markup.add(types.KeyboardButton(text=btn_cls.ADD_POSTCARD.value))
        markup.add(types.KeyboardButton(text=btn_cls.BACK.value))

        await message.answer(
            AdminPanelPostCardsHandler.Texts.POSTCARD_ADDED.value,
            reply_markup=markup,
        )
        logger.info("Added postcard %s" % postcard.name)

    @Handler.callback_query_handler(
        lambda callback_query: callback_query.data.startswith(
            "change_postcard_status:"
        )
    )
    @admin_only
    async def change_postcard_status(callback_query: types.CallbackQuery):
        """Change postcard status."""

        postcard = await PostCard(
            _id=ObjectId(callback_query.data.split(":")[1])
        ).get()
        postcard.is_active = not postcard.is_active
        await postcard.save()

        await Bot.get_current().edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=AdminPanelPostCardsHandler.get_options(postcard),
        )

    @Handler.callback_query_handler(
        lambda callback_query: callback_query.data.startswith("edit_postcard:")
    )
    @admin_only
    async def edit_postcard(callback_query: types.CallbackQuery):
        """Edit postcard."""

        postcard = await PostCard(
            _id=ObjectId(callback_query.data.split(":")[1])
        ).get()
        await PostCardEditForm.name.set()

        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data["postcard"] = postcard

        await Bot.get_current().send_message(
            chat_id=callback_query.message.chat.id,
            text=AdminPanelPostCardsHandler.Texts.EDIT_NAME.value.format(
                name=md.bold(postcard.name)
            ),
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(
        content_types=types.ContentType.TEXT, state=PostCardEditForm.name
    )
    @admin_only
    async def process_edit_postcard_name(
        message: types.Message, state: FSMContext
    ):
        """Postcard name."""

        async with state.proxy() as data:
            data["name"] = message.text

        await PostCardEditForm.description.set()
        await message.answer(
            AdminPanelPostCardsHandler.Texts.EDIT_DESCRIPTION.value.format(
                description=md.bold(data["postcard"].description)
            ),
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(
        content_types=types.ContentType.TEXT,
        state=PostCardEditForm.description,
    )
    @admin_only
    async def process_edit_postcard_description(
        message: types.Message, state: FSMContext
    ):
        """Postcard description."""

        async with state.proxy() as data:
            data["description"] = message.text

        await PostCardEditForm.image.set()
        await message.answer_photo(
            photo=data["postcard"].thumbnail,
            caption=AdminPanelPostCardsHandler.Texts.EDIT_IMAGE.value,
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(
        content_types=types.ContentType.PHOTO, state=PostCardEditForm.image
    )
    @admin_only
    async def process_edit_postcard_image(
        message: types.Message, state: FSMContext
    ):
        """Postcard image."""

        await AdminPanelPostCardsHandler.save_updated_data(message, state)

        await state.finish()

        btn_cls = AdminPanelPostCardsHandler.Buttons
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        markup.add(types.KeyboardButton(text=btn_cls.ADD_POSTCARD.value))
        markup.add(types.KeyboardButton(text=btn_cls.BACK.value))

        await message.answer(
            AdminPanelPostCardsHandler.Texts.POSTCARD_ADDED.value,
            reply_markup=markup,
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.callback_query_handler(Text(startswith="delete_postcard:"))
    @admin_only
    async def delete_postcard(callback_query: types.CallbackQuery):
        """Delete postcard."""

        await Bot.get_current().edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text=AdminPanelPostCardsHandler.Buttons.YES.value,
                            callback_data="confirm_delete_postcard:"
                            + callback_query.data.split(":")[1],
                        ),
                        types.InlineKeyboardButton(
                            text=AdminPanelPostCardsHandler.Buttons.NO.value,
                            callback_data="cancel_delete_postcard:"
                            + callback_query.data.split(":")[1],
                        ),
                    ]
                ]
            ),
        )

    @Handler.callback_query_handler(
        Text(startswith="confirm_delete_postcard:")
    )
    @admin_only
    async def confirm_delete_postcard(callback_query: types.CallbackQuery):
        """Confirm postcard deletion."""

        postcard = await PostCard(
            _id=ObjectId(callback_query.data.split(":")[1])
        ).get()
        await postcard.delete()

        await Bot.get_current().edit_message_caption(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            caption=(
                AdminPanelPostCardsHandler.Texts.POSTCARD_DELETED.value.format(
                    name=md.bold(postcard.name)
                )
            ),
            reply_markup=types.InlineKeyboardMarkup(),
        )

    @Handler.callback_query_handler(Text(startswith="cancel_delete_postcard:"))
    @admin_only
    async def cancel_delete_postcard(callback_query: types.CallbackQuery):
        """Cancel postcard deletion."""

        postcard = await PostCard(
            _id=ObjectId(callback_query.data.split(":")[1])
        ).get()
        await Bot.get_current().edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=AdminPanelPostCardsHandler.get_options(postcard),
        )
