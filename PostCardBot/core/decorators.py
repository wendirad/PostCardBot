"""Decorators for the PostCardBot."""

from aiogram import Dispatcher


class Handler:

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
