"""
    probot/adapters/wsgi/base
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Contains base types to be used/extended by WSGI adapters.
"""
import abc

from ... import models
from ...hints import ProbotSyncHandler
from .. import base


class WSGIAdapter(base.Adapter[base.AppT, base.RequestT, base.ResponseT],
                  metaclass=abc.ABCMeta):
    """
    Synchronous adapter (WSGI) for handling HTTP requests/responses.
    """
    @abc.abstractmethod
    def register(self, handler: ProbotSyncHandler) -> None:
        """
        Register request handler function for the adapter.

        :param handler: Handler function to be called for each request
        :return: Nothing
        """
        raise NotImplementedError('Must be implemented by derived class')

    @abc.abstractmethod
    def translate(self, handler: ProbotSyncHandler) -> base.ResponseT:
        """
        Wraps handler to translate adapter specific HTTP requests/responses
        before delegating business logic to handler function.

        :param handler: Handler function to wrap
        :return: Response to return
        """
        raise NotImplementedError('Must be implemented by derived class')

    @abc.abstractmethod
    def translate_request(self, request: base.RequestT) -> models.Request:
        """
        Translate an adapter specific request into a probot request.

        :param request: Adapter specific request
        :return: Probot request
        """
        raise NotImplementedError('Must be implemented by derived class')

    @abc.abstractmethod
    def translate_response(self, response: models.Response) -> base.ResponseT:
        """
        Translate a probot response into an adapter specific response.

        :param response: Probot response
        :return: Adapter specific response
        """
        raise NotImplementedError('Must be implemented by derived class')
