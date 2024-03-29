"""
    probot/asgi/aiohttp
    ~~~~~~~~~~~~~~~~~~~

    Contains asynchronous adapter using `aiohttp`.
"""
from typing import Awaitable, Callable

from aiohttp import web

from .. import base, models
from ..hints import LifecycleEventHandlerResponse, ProbotAsyncHandler, ProbotAsyncLifecycleEventHandler
from . import adapter, app

AdapterApp = web.Application
AdapterRequest = web.Request
AdapterResponse = web.Response


class Adapter(adapter.Adapter[AdapterApp, AdapterRequest, AdapterResponse]):
    """
    AIOHTTP adapter for handling HTTP requests/responses.
    """
    def register(self, handler: ProbotAsyncHandler) -> None:
        """
        Register request handler function for the adapter.

        :param handler: Handler function to be called for each request
        :return: Nothing
        """
        self.app.add_routes([web.post(self.path, self.translate(handler))])

    def register_lifecycle_event(self,
                                 event: models.LifecycleEvent,
                                 handler: ProbotAsyncLifecycleEventHandler) -> None:
        """
        Register lifecycle event handler function for the adapter.

        :param event: Lifecycle event to register handler for
        :param handler: Handler function to be called for the given lifecycle event
        :return: Nothing
        """
        self.app.on_startup.append(self.translate_lifecycle_event(event, handler))
        self.app.on_shutdown.append(self.translate_lifecycle_event(event, handler))

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
        async def wrapper(_app: AdapterApp):
            return await handler(event)
        return wrapper

    def translate(self, handler: ProbotAsyncHandler) -> Callable[[AdapterRequest], Awaitable[AdapterResponse]]:
        """
        Translate AIOHTTP HTTP requests/responses before delegating
        business logic to handler function.

        :param handler: Handler function to wrap
        :return: Response to return
        """
        async def wrapper(request: AdapterRequest) -> AdapterResponse:
            native_request = await self.translate_request(request)
            response = await handler(native_request)
            return await self.translate_response(response)
        return wrapper

    async def translate_request(self, request: AdapterRequest) -> models.Request:
        """
        Translate a AIOHTTP request into a probot request.

        :param request: AIOHTTP request
        :return: Probot request
        """
        body = await request.read()
        json = await request.json()

        # TODO: Translate query/headers to proper structure.

        return models.Request(
            method=request.method,
            body_raw=body,
            body_json=json,
            query=request.query,
            headers=request.headers
        )

    async def translate_response(self, response: models.Response) -> AdapterResponse:
        """
        Translate a probot response into a AIOHTTP response.

        :param response: Probot response
        :return: AIOHTTP response
        """
        return web.Response(
            status=response.status_code,
            body=response.content,
            headers=response.headers
        )


App = app.App[Adapter]


class Probot(base.Probot[App, Adapter, AdapterApp]):
    app_cls = App
    adapter_cls = Adapter
