"""Core model for the PostCardBot."""


import json
from datetime import datetime

from aiogram.types import User as TelegramUser

import babel

from PostCardBot.core.db import Database


class BaseModel:
    def __init_subclass__(cls, **kwargs):
        """
        Initialize the subclass.
        """
        super().__init_subclass__(**kwargs)
        cls.meta = cls.Meta()
        cls.meta.model = cls
        cls.meta.model_name = cls.__name__

    class Meta:
        """
        Meta class for the model.
        """

        pass

    def __init__(self, **kwargs):
        """
        Initialize the model.
        """
        self.kwargs = kwargs
        for field in self.meta.fields:
            value = kwargs.get(field)
            if value is None:
                default = getattr(self, field, None)
                if callable(default):
                    value = default()
                else:
                    value = default
            setattr(self, field, value)

    def __repr__(self):
        """
        Represent the model.
        """
        return f"<{self.meta.model_name} {getattr(self, self.pk_field)} >"

    def __str__(self):
        """
        String representation of the model.
        """
        return f"{self.meta.model_name} {getattr(self, self.pk_field)}"

    def to_dict(self):
        """
        Convert the model to a dictionary.
        """
        return {field: getattr(self, field) for field in self.meta.fields}

    def to_json(self):
        """
        Convert the model to a JSON string.
        """
        return json.dumps(self.to_dict())

    def to_python(self):
        """
        Convert the model to a Python dictionary.
        """
        return self.to_dict()

    @classmethod
    def from_dict(cls, data):
        """
        Convert a dictionary to a model.
        """
        return cls(**data)

    @classmethod
    def from_json(cls, data):
        """
        Convert a JSON string to a model.
        """
        return cls.from_dict(json.loads(data))


class DatabaseModel(BaseModel):
    """
    Database model for the PostCardBot.
    """

    db = Database()

    def __init__(self, **kwargs):
        """
        Initialize the model.
        """
        super().__init__(**kwargs)
        if self.pk_field not in self.meta.fields:
            self.meta.fields.append(self.pk_field)

    def __new__(cls, *args, **kwargs):
        """
        Create a new model.
        """
        if not hasattr(cls, "collection"):
            cls.collection = cls.db.get_collection(cls.meta.collection_name)
        return super().__new__(cls)

    async def save(self):
        """
        Save the model to the database.
        """
        data = {
            key: value
            for key, value in self.to_dict().items()
            if key in self.kwargs
        }
        pk = data.pop(self.pk_field, None)
        defaults = {
            key: value
            for key, value in self.to_dict().items()
            if key not in self.kwargs
        }
        await self.collection.update_one(
            {self.pk_field: pk},
            {
                "$set": data,
                "$currentDate": {
                    "lastModified": True,
                },
                "$setOnInsert": {
                    **defaults,
                    "created": datetime.utcnow(),
                },
            },
            upsert=True,
        )
        return await self.get()

    async def delete(self):
        """
        Delete the model from the database.
        """
        await self.collection.delete_one({self.pk_field: self.pk})

    async def get(self):
        """
        Get the model from the database.
        """
        data = await self.collection.find_one({self.pk_field: self.pk})
        if data:
            return self.from_dict(data)

    @classmethod
    async def all(cls):
        """
        Get all models from the database.
        """
        if not hasattr(cls, "collection"):
            cls.collection = cls.db.get_collection(cls.meta.collection_name)
        data = cls.collection.find({})
        return [cls.from_dict(d) async for d in data]

    @classmethod
    async def count(cls):
        """
        Get the number of models in the database.
        """
        if not hasattr(cls, "collection"):
            cls.collection = cls.db.get_collection(cls.meta.collection_name)
        return cls.collection.count_documents({})

    @classmethod
    async def filter(cls, **kwargs):
        """
        Get all models from the database that match the filter.
        """
        data = await cls.collection.find(kwargs)
        return [cls.from_dict(d) for d in data]

    async def get_or_create(self, **kwargs):
        """
        Get the model from the database or create a new one.
        """

        document = await self.get()
        if document:
            return document
        else:
            return await self.save()

    @property
    def pk(self):
        """
        Get the primary key of the model.
        """
        return getattr(self, self.pk_field, None)

    @property
    def pk_field(self):
        """
        Get the primary key field of the model.
        """
        return self.meta.pk_field

    class Meta:
        pk_field = "_id"
        collection_name = None
        fields = []


class User(DatabaseModel, TelegramUser):
    """User model."""

    selected_language = "en"
    is_admin = False
    is_superuser = False
    is_active = False

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
            "is_admin",
            "is_superuser",
            "is_active",
            "added_to_attachment_menu",
            "can_join_groups",
            "can_read_all_group_messages",
            "supports_inline_queries",
            "created",
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
