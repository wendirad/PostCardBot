import enum

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentTypes

from bson import ObjectId
from loguru import logger

from PostCardBot.core import config
from PostCardBot.core.decorators import Handler, admin_only
from PostCardBot.core.handlers import BaseHandler
from PostCardBot.models import Category

_ = config.i18n.gettext
__ = config.i18n.lazy_gettext


class CategoryAddForm(StatesGroup):
    """Category add form."""

    name = State()
    description = State()


class CategoryEditForm(StatesGroup):
    """Category edit form."""

    name = State()
    description = State()


class CategoryHandler(BaseHandler):
    """Category handler."""

    class Buttons(enum.Enum):
        """Admin panel buttons."""

        POSTCARDS = _("📦 Postcards")
        CATEGORIES = _("📁 Categories")
        ADD_CATEGORY = _("➕📁 Add category")
        BACK_TO_CATEGORIES = _("🔙📁 Back to categories")
        BACK = _("🔙🔐 Admin panel")
        EDIT = "📝 Edit"
        DELETE = "🗑 Delete"
        YES = "✅ Yes"
        NO = "❌ No"
        ACTIVATE = "✅ Activate"
        DEACTIVATE = "❌ Deactivate"

    class Texts(enum.Enum):
        """Category texts."""

        ENTER_NAME = _("Enter category name\n\n Type /cancel to cancel")
        ENTER_DESCRIPTION = _(
            "Enter category description\n\n Type /cancel to cancel"
        )
        EDIT_NAME = _(
            "{name}\n\nEnter new category name\n\ntype "
            "/cancel to cancel /skip to skip chaning name."
        )
        EDIT_DESCRIPTION = _(
            "{description}\n\nEnter new category description\n\n type "
            "/cancel to cancel or /skip to skip changing description."
        )
        CATEGORY_ADDED = _("Category added successfully.")
        CATEGORY_EDITED = _("Category edited successfully.")
        CONFIRM_DELETE = _("Are you sure you want to delete this category?")
        CATEGORY_DELETED = _("Category deleted successfully.")
        CATEGORY_NOT_FOUND = _("Category not found.")
        OPERAION_CANCELLED = _("Operation cancelled.")

    @staticmethod
    def get_options(category):
        btn_cls = CategoryHandler.Buttons
        return types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=btn_cls.POSTCARDS.value,
                        callback_data="categorical_postcards:"
                        + str(category.pk),
                    ),
                ],
                [
                    types.InlineKeyboardButton(
                        text=btn_cls.EDIT.value,
                        callback_data="edit_category:" + str(category.pk),
                    ),
                    types.InlineKeyboardButton(
                        text=btn_cls.DELETE.value,
                        callback_data="delete_category:" + str(category.pk),
                    ),
                    types.InlineKeyboardButton(
                        text=btn_cls.DEACTIVATE.value
                        if category.is_active
                        else btn_cls.ACTIVATE.value,
                        callback_data="change_category_status:"
                        + str(category.pk),
                    ),
                ],
            ],
        )

    @staticmethod
    @admin_only
    async def save_updated_data(message, state):
        """Save updated data."""

        async with state.proxy() as data:
            category = await data["category"].save()

            btn_cls = CategoryHandler.Buttons

            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True
            )

            for button in [btn_cls.ADD_CATEGORY.value, btn_cls.BACK.value]:
                markup.add(types.KeyboardButton(text=button))

            await message.answer(
                CategoryHandler.Texts.CATEGORY_EDITED.value,
                reply_markup=markup,
            )
            await message.answer(
                text=__(category.name) + "\n\n" + category.description,
                reply_markup=CategoryHandler.get_options(category),
                parse_mode=types.ParseMode.MARKDOWN,
            )

            # Remove inline keyboard from the message
            await Bot.get_current().edit_message_reply_markup(
                chat_id=data["chat_id"],
                message_id=data["message_id"],
                reply_markup=None,
            )

    @Handler.message_handler(
        commands=["cancel"],
        state=[
            CategoryAddForm.name,
            CategoryAddForm.description,
            CategoryEditForm.name,
            CategoryEditForm.description,
        ],
    )
    @admin_only
    async def cancel(message: types.Message, state: FSMContext):
        """Cancel current operation."""

        logger.info("Cancelling state %r" % state)

        await state.finish()

        btn_cls = CategoryHandler.Buttons
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        markup.add(types.KeyboardButton(text=btn_cls.ADD_CATEGORY.value))
        markup.add(types.KeyboardButton(text=btn_cls.BACK.value))

        await message.answer(
            CategoryHandler.Texts.OPERAION_CANCELLED.value, reply_markup=markup
        )

    @Handler.message_handler(commands="skip", state=CategoryEditForm.name)
    @admin_only
    async def skip_edit_name(message: types.Message, state: FSMContext):
        """Skip changing category name."""

        async with state.proxy() as data:
            category = data["category"]

        await CategoryEditForm.next()
        await Bot.get_current().send_message(
            text=CategoryHandler.Texts.EDIT_DESCRIPTION.value.format(
                description=category.description
            ),
            chat_id=message.chat.id,
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(
        commands="skip", state=CategoryEditForm.description
    )
    @admin_only
    async def skip_edit_description(message: types.Message, state: FSMContext):
        """Skip changing category description."""

        await CategoryHandler.save_updated_data(message, state)

        await state.finish()

    @Handler.message_handler(Text(equals=__(Buttons.BACK_TO_CATEGORIES.value)))
    @Handler.message_handler(Text(equals=__(Buttons.CATEGORIES.value)))
    @admin_only
    async def categories(message: types.Message):
        """Postcards command handler."""

        btn_cls = CategoryHandler.Buttons
        button_markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.ADD_CATEGORY.value)),
        )
        button_markup.add(
            types.KeyboardButton(__(btn_cls.BACK.value)),
        )
        await message.answer(text=_("Categories"), reply_markup=button_markup)
        for category in await Category.all():
            await message.answer(
                text=md.bold(category.name)
                + "\n\n"
                + md.italic(category.description),
                reply_markup=CategoryHandler.get_options(category),
                parse_mode=types.ParseMode.MARKDOWN,
            )

    @Handler.callback_query_handler(Text(startswith="change_category_status:"))
    @admin_only
    async def change_status(callback_query: types.CallbackQuery):
        """Change category status."""

        category_id = ObjectId(callback_query.data.split(":")[1])
        category = await Category(_id=category_id).get()
        category.is_active = not category.is_active
        await category.save()

        await Bot.get_current().edit_message_reply_markup(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=CategoryHandler.get_options(category),
        )

    @Handler.message_handler(Text(equals=__(Buttons.ADD_CATEGORY.value)))
    @admin_only
    async def add_category(message: types.Message):
        """Add category."""

        await CategoryAddForm.first()
        await message.answer(
            CategoryHandler.Texts.ENTER_NAME.value,
            reply_markup=types.ReplyKeyboardRemove(),
        )

    @Handler.message_handler(
        content_types=ContentTypes.TEXT, state=CategoryAddForm.name
    )
    @admin_only
    async def process_category_name(message: types.Message, state: FSMContext):
        """Save category name."""

        async with state.proxy() as data:
            data["name"] = message.text

        await CategoryAddForm.next()
        await message.answer(
            CategoryHandler.Texts.ENTER_DESCRIPTION.value,
            reply_markup=types.ReplyKeyboardRemove(),
        )

    @Handler.message_handler(
        content_types=ContentTypes.TEXT, state=CategoryAddForm.description
    )
    @admin_only
    async def process_category_description(
        message: types.Message, state: FSMContext
    ):
        """Save category description."""

        async with state.proxy() as data:
            data["description"] = message.text
            category = await Category(
                name=data["name"], description=data["description"]
            ).save()

            await message.answer(
                text=__(category.name) + "\n\n" + category.description,
                reply_markup=CategoryHandler.get_options(category),
                parse_mode=types.ParseMode.MARKDOWN,
            )

        await state.finish()

        btn_cls = CategoryHandler.Buttons
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        markup.add(types.KeyboardButton(text=btn_cls.ADD_CATEGORY.value))
        markup.add(types.KeyboardButton(text=btn_cls.BACK.value))

        await message.answer(
            CategoryHandler.Texts.CATEGORY_ADDED.value, reply_markup=markup
        )

    @Handler.callback_query_handler(Text(startswith="edit_category:"))
    @admin_only
    async def edit_category(callback_query: types.CallbackQuery):
        """Edit category."""

        await CategoryEditForm.first()
        dp = Dispatcher.get_current()
        state = dp.current_state()

        async with state.proxy() as data:
            data["category"] = await Category(
                _id=ObjectId(callback_query.data.split(":")[1])
            ).get()
            data["message_id"] = callback_query.message.message_id
            data["chat_id"] = callback_query.message.chat.id

        await Bot.get_current().send_message(
            text=CategoryHandler.Texts.EDIT_NAME.format(
                name=md.italic(data["category"].name)
            ),
            chat_id=callback_query.message.chat.id,
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(
        content_types=ContentTypes.TEXT, state=CategoryEditForm.name
    )
    @admin_only
    async def process_edit_name(message: types.Message, state: FSMContext):
        """Save edited category name."""

        async with state.proxy() as data:
            data["category"].name = message.text

        await CategoryEditForm.next()
        await Bot.get_current().send_message(
            text=CategoryHandler.Texts.EDIT_DESCRIPTION.value.format(
                description=md.italic(data["category"].description)
            ),
            chat_id=message.chat.id,
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode=types.ParseMode.MARKDOWN,
        )

    @Handler.message_handler(
        content_types=ContentTypes.TEXT, state=CategoryEditForm.description
    )
    @admin_only
    async def process_edit_description(
        message: types.Message, state: FSMContext
    ):
        """Save edited category description."""

        async with state.proxy() as data:
            data["category"].description = message.text

        await CategoryHandler.save_updated_data(message, state)

        await state.finish()

        btn_cls = CategoryHandler.Buttons
        markup = types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=True
        )
        markup.add(types.KeyboardButton(text=btn_cls.ADD_CATEGORY.value))
        markup.add(types.KeyboardButton(text=btn_cls.BACK.value))

        await message.answer(
            CategoryHandler.Texts.CATEGORY_EDITED.value, reply_markup=markup
        )

    @Handler.callback_query_handler(Text(startswith="delete_category:"))
    @admin_only
    async def delete_category(callback_query: types.CallbackQuery):
        """confirm category deletion."""

        btn_cls = CategoryHandler.Buttons
        markup = (
            types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text=btn_cls.YES.value,
                            callback_data="confirm_delete_category:"
                            + callback_query.data.split(":")[1],
                        ),
                        types.InlineKeyboardButton(
                            text=btn_cls.NO.value,
                            callback_data="cancel_delete_category:"
                            + callback_query.data.split(":")[1],
                        ),
                    ],
                ],
            ),
        )
        await Bot.get_current().edit_message_text(
            text=CategoryHandler.Texts.CONFIRM_DELETE.value,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=markup,
        )

    @Handler.callback_query_handler(
        Text(startswith="confirm_delete_category:")
    )
    @admin_only
    async def confirm_delete(callback_query: types.CallbackQuery):
        """Confirm delete category."""

        category = Category(_id=ObjectId(callback_query.data.split(":")[1]))
        bot = Bot.get_current()
        if category:
            await category.delete()
            await bot.edit_message_text(
                text=CategoryHandler.Texts.CATEGORY_DELETED.value,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
            )
        else:
            await bot.answer_callback_query(
                callback_query.id,
                text=CategoryHandler.Texts.CATEGORY_NOT_FOUND.value,
            )

    @Handler.callback_query_handler(Text(startswith="cancel_delete_category:"))
    @admin_only
    async def cancel_delete_category(callback_query: types.CallbackQuery):
        """Cancel category deletion."""

        category_id = ObjectId(callback_query.data.split(":")[1])
        category = await Category(_id=category_id).get()

        await Bot.get_current().edit_message_text(
            text=__(category.name) + "\n\n" + category.description,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            reply_markup=CategoryHandler.get_options(category),
            parse_mode=types.ParseMode.MARKDOWN,
        )
        logger.info(
            "Cancelled category deletion for category %s" % category.name
        )
