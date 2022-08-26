"""Decorators for the PostCardBot."""

import functools

from aiogram import Dispatcher, types


class Handler:
    """Handler class for the bot."""

    dp = Dispatcher.get_current()

    @classmethod
    def message_handler(
        cls,
        *custom_filters,
        commands=None,
        regexp=None,
        content_types=None,
        state=None,
        run_task=None,
        **kwargs,
    ):
        """
        Decorator for message handlers.
        """

        def decorator(callback):
            if isinstance(callback, staticmethod):
                callback = callback.__func__
            cls.dp.register_message_handler(
                callback,
                *custom_filters,
                commands=commands,
                regexp=regexp,
                content_types=content_types,
                state=state,
                run_task=run_task,
                **kwargs,
            )
            return staticmethod(callback)

        return decorator

    @classmethod
    def callback_query_handler(
        cls,
        *custom_filters,
        commands=None,
        regexp=None,
        content_types=None,
        state=None,
        run_task=None,
        **kwargs,
    ):
        """
        Decorator for callback query handlers.
        """

        def decorator(callback):
            if isinstance(callback, staticmethod):
                callback = callback.__func__
            cls.dp.register_callback_query_handler(
                callback,
                *custom_filters,
                commands=commands,
                regexp=regexp,
                content_types=content_types,
                state=state,
                run_task=run_task,
                **kwargs,
            )
            return staticmethod(callback)

        return decorator


def admin_only(callback):
    """
    Decorator for admin only handlers.
    """

    @functools.wraps(callback)
    async def wrapper(message: types.Message, **kwargs):
        """
        Admin only wrapper.
        """

        if message.from_user.is_superuser or message.from_user.is_admin:
            return await callback(message, **kwargs)

    return wrapper


def superuser_only(callback):
    """
    Decorator for superuser only handlers.
    """

    @functools.wraps(callback)
    async def wrapper(message: types.Message, **kwargs):
        """
        Superuser only wrapper.
        """

        if message.from_user.is_superuser:
            return await callback(message, **kwargs)

    return wrapper
