"""PostCardBot postcard model."""

from PostCardBot.core.model import DatabaseModel


class Category(DatabaseModel):
    """PostCardBot postcard category model."""

    is_active = True

    class Meta(DatabaseModel.Meta):
        collection_name = "category"
        model_name = "category"
        fields = ["name", "description", "is_active"]


class PostCard(DatabaseModel):
    """PostCardBot postcard model."""

    is_active = True

    class Meta(DatabaseModel.Meta):
        collection_name = "postcard"
        model_name = "postcard"
        fields = [
            "name",
            "description",
            "is_active",
            "category_id",
            "image",
            "thumbnail",
        ]
