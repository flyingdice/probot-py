"""
    probot/adapters/wsgi/flask
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Contains synchronous adapter using `flask`.
"""
from typing import Callable

import flask

from .. import base, models
from ..hints import ProbotSyncHandler, ProbotSyncLifecycleEventHandler
from . import adapter, app

AdapterApp = flask.Flask
AdapterRequest = flask.Request
AdapterResponse = flask.Response


class Adapter(adapter.Adapter[AdapterApp, AdapterRequest, AdapterResponse]):
    """
    Flask adapter for handling HTTP requests/responses.
    """
    def register(self, handler: ProbotSyncHandler) -> None:
        """
        Register request handler function for the adapter.

        :param handler: Handler function to be called for each request
        :return: Nothing
        """
        self.app.route(self.path, methods=self.methods)(self.translate(handler))

    def register_lifecycle_event(self,
                                 event: models.LifecycleEvent,
                                 handler: ProbotSyncLifecycleEventHandler) -> None:
        """
        Register lifecycle event handler function for the adapter.

        :param event: Lifecycle event to register handler for
        :param handler: Handler function to be called for the given lifecycle event
        :return: Nothing
        """
        raise NotImplementedError('Flask lifecycle events not implemented')

    def translate(self, handler: ProbotSyncHandler) -> Callable[[AdapterRequest], AdapterResponse]:
        """
        Translate Flask HTTP requests/responses before delegating
        business logic to handler function.

        :param handler: Handler function to wrap
        :return: Response to return
        """
        def wrapper() -> flask.Response:
            native_request = self.translate_request(flask.request)
            response = handler(native_request)
            return self.translate_response(response)
        return wrapper

    def translate_request(self, request: AdapterRequest) -> models.Request:
        """
        Translate a Flask request into a probot request.

        :param request: Flask request
        :return: Probot request
        """
        body = request.get_data()
        json = request.get_json()

        # TODO: Translate query/headers to proper structure.

        return models.Request(
            method=request.method,
            body_raw=body,
            body_json=json,
            query=request.args,
            headers=request.headers
        )

    def translate_response(self, response: models.Response) -> AdapterResponse:
        """
        Translate a probot response into a Flask response.

        :param response: Probot response
        :return: Flask response
        """
        return flask.make_response(
            response.content,
            response.status_code,
            response.headers
        )


App = app.App[Adapter]


class Probot(base.Probot[App, Adapter, AdapterApp]):
    app_cls = App
    adapter_cls = Adapter
