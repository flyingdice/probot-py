"""
    probot/asgi/fastapi
    ~~~~~~~~~~~~~~~~~~~

    Contains asynchronous adapter using `fastapi`.
"""
from typing import Awaitable, Callable

import fastapi

from .. import models, base
from ..hints import LifecycleEventHandlerResponse, ProbotAsyncLifecycleEventHandler, ProbotAsyncHandler
from . import adapter, app

AdapterApp = fastapi.FastAPI
AdapterRequest = fastapi.Request
AdapterResponse = fastapi.Response


class Adapter(adapter.Adapter[AdapterApp, AdapterRequest, AdapterResponse]):
    """
    FastAPI adapter for handling HTTP requests/responses.
    """
    def register(self, handler: ProbotAsyncHandler) -> None:
        """
        Register request handler function for the adapter.

        :param handler: Handler function to be called for each request
        :return: Nothing
        """
        self.app.post(self.path)(self.translate(handler))

    def register_lifecycle_event(self,
                                 event: models.LifecycleEvent,
                                 handler: ProbotAsyncLifecycleEventHandler) -> None:
        """
        Register lifecycle event handler function for the adapter.

        :param event: Lifecycle event to register handler for
        :param handler: Handler function to be called for the given lifecycle event
        :return: Nothing
        """
        self.app.on_event(event.value)(self.translate_lifecycle_event(event, handler))

    @staticmethod
    def translate_lifecycle_event(
        event: models.LifecycleEvent,
        handler: ProbotAsyncLifecycleEventHandler
    ) -> Callable[[], Awaitable[LifecycleEventHandlerResponse]]:
        """
        Translate lifecycle events and delegate into Probot lifecycle event handlers.

        :param event: Lifecycle event to translate
        :param handler: Handler function to wrap
        :return: Wrapper function
        """
        async def wrapper():
            return await handler(event)
        return wrapper

    def translate(self, handler: ProbotAsyncHandler) -> Callable[[AdapterRequest], Awaitable[AdapterResponse]]:
        """
        Translate FastAPI HTTP requests/responses before delegating
        business logic to handler function.

        :param handler: Handler function to wrap
        :return: Wrapper function
        """
        async def wrapper(request: fastapi.Request) -> fastapi.Response:
            native_request = await self.translate_request(request)
            response = await handler(native_request)
            return await self.translate_response(response)
        return wrapper

    async def translate_request(self, request: AdapterRequest) -> models.Request:
        """
        Translate a FastAPI request into a probot request.

        :param request: FastAPI request
        :return: Probot request
        """
        body = await request.body()
        json = await request.json()

        # TODO: Translate query/headers to proper structure.

        return models.Request(
            method=request.method,
            body_raw=body,
            body_json=json,
            query=request.query_params,
            headers=request.headers
        )

    async def translate_response(self, response: models.Response) -> AdapterResponse:
        """
        Translate a probot response into a FastAPI response.

        :param response: Probot response
        :return: FastAPI response
        """
        return fastapi.Response(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers
        )


App = app.App[Adapter]


class Probot(base.Probot[App, Adapter, AdapterApp]):
    app_cls = App
    adapter_cls = Adapter
