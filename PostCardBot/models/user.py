"""User model."""

from aiogram.types import User as TelegramUser

import babel

from PostCardBot.core.model import DatabaseModel


class User(DatabaseModel, TelegramUser):
    """User model."""

    selected_language = "en"

    class Meta:
        collection_name = "user"
        model_name = "user"
        pk_field = "id"
        fields = [
            "id",
            "first_name",
            "last_name",
            "username",
            "language_code",
            "selected_language",
            "is_bot",
            "is_premium",
            "added_to_attachment_menu",
            "can_join_groups",
            "can_read_all_group_messages",
            "supports_inline_queries",
        ]

    @property
    def locale(self):
        """Get the locale for the user."""

        if not (self.selected_language or self.language_code):
            return None
        if not hasattr(self, "_locale"):
            setattr(
                self,
                "_locale",
                babel.core.Locale.parse(
                    self.selected_language or self.language_code, sep="-"
                ),
            )
        return getattr(self, "_locale")
