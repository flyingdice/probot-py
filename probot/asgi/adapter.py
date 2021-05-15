"""
    probot/asgi/adapter
    ~~~~~~~~~~~~~~~~~~~

    Contains abstract ASGI (async) adapter.
"""
import abc
from typing import Awaitable, Callable, TypeVar

from .. import models
from ..hints import LifecycleEventHandlerResponse, ProbotAsyncHandler, ProbotAsyncLifecycleEventHandler
from .. import base


class Adapter(base.Adapter[base.AdapterAppT, base.AdapterRequestT, base.AdapterResponseT],
              metaclass=abc.ABCMeta):
    """
    Asynchronous adapter (ASGI) for handling HTTP requests/responses.
    """
    @abc.abstractmethod
    def register(self, handler: ProbotAsyncHandler) -> None:
        """
        Register request handler function for the adapter.

        :param handler: Handler function to be called for each request
        :return: Nothing
        """
        raise NotImplementedError('Must be implemented by derived class')

    @abc.abstractmethod
    def register_lifecycle_event(self,
                                 event: models.LifecycleEvent,
                                 handler: ProbotAsyncLifecycleEventHandler) -> None:
        """
        Register lifecycle event handler function for the adapter.

        :param event: Lifecycle event to register handler for
        :param handler: Handler function to be called for the given lifecycle event
        :return: Nothing
        """
        raise NotImplementedError('Must be implemented by derived class')

    @abc.abstractmethod
    async def translate(self, handler: ProbotAsyncHandler) -> base.AdapterResponseT:
        """
        Wraps handler to translate adapter specific HTTP requests/responses
        before delegating business logic to handler function.

        :param handler: Handler function to wrap
        :return: Response to return
        """
        raise NotImplementedError('Must be implemented by derived class')

    @abc.abstractmethod
    async def translate_request(self, request: base.AdapterRequestT) -> models.Request:
        """
        Translate an adapter specific request into a probot request.

        :param request: Adapter specific request
        :return: Probot request
        """
        raise NotImplementedError('Must be implemented by derived class')

    @abc.abstractmethod
    def translate_response(self, response: models.Response) -> base.AdapterResponseT:
        """
        Translate a probot response into an adapter specific response.

        :param response: Probot response
        :return: Adapter specific response
        """
        raise NotImplementedError('Must be implemented by derived class')


ASGIAdapterT = TypeVar('ASGIAdapterT', bound=Adapter)
