"""Core model for the PostCardBot."""

import json

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
            setattr(self, field, kwargs.get(field, getattr(self, field, None)))

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
        self.collection = self.db.get_collection(self.meta.collection_name)
        if self.pk_field not in self.meta.fields:
            self.meta.fields.append(self.pk_field)

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
        await self.collection.update_one(
            {self.pk_field: pk}, {"$set": data}, upsert=True
        )

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
        return self.from_dict(data)

    @classmethod
    async def all(cls):
        """
        Get all models from the database.
        """
        data = await cls.collection.find({})
        return [cls.from_dict(d) for d in data]

    @classmethod
    async def filter(cls, **kwargs):
        """
        Get all models from the database that match the filter.
        """
        data = await cls.collection.find(kwargs)
        return [cls.from_dict(d) for d in data]

    @classmethod
    async def get_or_create(cls, **kwargs):
        """
        Get the model from the database or create a new one.
        """
        data = await cls.collection.find_one(kwargs)
        if data:
            return cls.from_dict(data)
        else:
            return cls(**kwargs)

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
