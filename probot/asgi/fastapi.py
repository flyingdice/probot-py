"""
    probot/asgi/fastapi
    ~~~~~~~~~~~~~~~~~~~

    Contains asynchronous adapter using `fastapi`.
"""
from typing import Awaitable, Callable

import fastapi

from .. import models, base
from ..hints import ProbotAsyncHandler
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

    def translate(self, handler: ProbotAsyncHandler) -> Callable[[AdapterRequest], Awaitable[AdapterResponse]]:
        """
        Translate FastAPI HTTP requests/responses before delegating
        business logic to handler function.

        :param handler: Handler function to wrap
        :return: Response to return
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
