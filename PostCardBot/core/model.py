"""Core model for the PostCardBot."""

import json


class BaseModel:
    def __init_subclass__(cls, **kwargs):
        """
        Initialize the subclass.
        """
        super().__init_subclass__(**kwargs)
        cls.meta = cls.Meta()
        cls.meta.model = cls
        cls.meta.model_name = cls.__name__
        cls.meta.fields = []
        for field in cls.__annotations__:
            cls.meta.fields.append(field)

    class Meta:
        """
        Meta class for the model.
        """

        pass

    def __init__(self, **kwargs):
        """
        Initialize the model.
        """
        for field in self.meta.fields:
            setattr(self, field, kwargs.get(field, None))

    def __repr__(self):
        """
        Represent the model.
        """
        return f"<{self.meta.model_name}>"

    def __str__(self):
        """
        String representation of the model.
        """
        return f"{self.meta.model_name}"

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
