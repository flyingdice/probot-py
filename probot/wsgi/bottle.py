"""
    probot/adapters/wsgi/bottle
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Contains synchronous adapter using `bottle`.
"""
from typing import Callable

import bottle

from .. import base, models
from ..hints import ProbotSyncHandler, ProbotSyncLifecycleEventHandler
from . import adapter, app

AdapterApp = bottle.Bottle
AdapterRequest = bottle.Request
AdapterResponse = bottle.Response


class Adapter(adapter.Adapter[AdapterApp, AdapterRequest, AdapterResponse]):
    """
    Bottle adapter for handling HTTP requests/responses.
    """
    def register(self, handler: ProbotSyncHandler) -> None:
        """
        Register request handler function for the adapter.

        :param handler: Handler function to be called for each request
        :return: Nothing
        """
        self.app.post(self.path)(self.translate(handler))

    def register_lifecycle_event(self,
                                 event: models.LifecycleEvent,
                                 handler: ProbotSyncLifecycleEventHandler) -> None:
        """
        Register lifecycle event handler function for the adapter.

        :param event: Lifecycle event to register handler for
        :param handler: Handler function to be called for the given lifecycle event
        :return: Nothing
        """
        raise NotImplementedError('Bottle lifecycle events not implemented')

    def translate(self, handler: ProbotSyncHandler) -> Callable[[AdapterRequest], AdapterResponse]:
        """
        Translate Bottle HTTP requests/responses before delegating
        business logic to handler function.

        :param handler: Handler function to wrap
        :return: Response to return
        """
        def wrapper() -> bottle.Response:
            native_request = self.translate_request(bottle.request)
            response = handler(native_request)
            return self.translate_response(response)
        return wrapper

    def translate_request(self, request: AdapterRequest) -> models.Request:
        """
        Translate a Bottle request into a probot request.

        :param request: Bottle request
        :return: Probot request
        """
        body = request.body.read()
        json = request.json

        return models.Request(
            method=request.method,
            body_raw=body,
            body_json=json,
            query=request.query,
            headers=request.headers
        )

    def translate_response(self, response: models.Response) -> AdapterResponse:
        """
        Translate a probot response into a Bottle response.

        :param response: Probot response
        :return: Bottle response
        """
        return bottle.Response(
            response.content,
            response.status_code,
            response.headers
        )


App = app.App[Adapter]


class Probot(base.Probot[App, Adapter, AdapterApp]):
    app_cls = App
    adapter_cls = Adapter
