"""Databaes module for PostCardBot."""

import motor.motor_asyncio
from loguru import logger
from pymongo.server_api import ServerApi

from PostCardBot.core import config


class SingletonClass:
    """
    Singleton class.
    """

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the class.
        """
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance


class Database(SingletonClass):
    def __init__(self):
        """
        Initialize the database.
        """
        logger.info("Initializing database.")
        self.db = self.get_database()

    def get_client(self):
        """
        Get the client for the database.
        """
        logger.info("Getting client for database.")
        return motor.motor_asyncio.AsyncIOMotorClient(
            config.DATABASE_URL,
            serverSelectionTimeoutMS=config.DATABASE_SELECTION_TIMEOUT,
            server_api=ServerApi("1"),
        )

    def get_database(self):
        """
        Get the database for the database.
        """
        logger.info("Getting database for database.")
        return self.get_client().get_database(config.DATABASE_NAME)

    def get_collection(self, collection_name):
        """
        Get the collection for the database.
        """
        logger.info(f"Getting collection for database: {collection_name}.")
        return self.db.get_collection(collection_name)
