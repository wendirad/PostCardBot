"""Decorators for the PostCardBot."""

import functools

from loguru import logger


async def message_handler(func, *d_args, **d_kwargs):
    """
    Decorator for message handlers.
    """

    @functools.wraps(func)
    async def wrapper(self, message, *args, **kwargs):
        """
        Wrapper for message handlers.
        """
        self.dp.register_message_handler(func, *d_args, **d_kwargs)
        logger.info(f"Message handler: {func.__name__}")
        return await func(self, message, *args, **kwargs)

    return wrapper


async def callback_query_handler(func, *d_args, **d_kwargs):
    """
    Decorator for callback query handlers.
    """

    @functools.wraps(func)
    async def wrapper(self, callback_query, *args, **kwargs):
        """
        Wrapper for callback query handlers.
        """
        self.dp.register_callback_query_handler(func, *d_args, **d_kwargs)
        logger.info(f"Callback query handler: {func.__name__}")
        return await func(self, callback_query, *args, **kwargs)

    return wrapper
