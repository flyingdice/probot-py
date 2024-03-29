"""
    probot/asgi
    ~~~~~~~~~~~

    Contains HTTP application for use with ASGI (async) adapters.
"""
import inspect

from .. import base, errors, models
from ..hints import AsyncEventHandler, AsyncEventMiddleware
from . import adapter


class App(base.App[adapter.ASGIAdapterT, AsyncEventHandler]):
    """
    App for ASGI (async) adapters.
    """
    async def on_lifecycle_event(self, event: models.LifecycleEvent) -> None:
        """
        Handler function called for each lifecycle event.

        This is responsible for invoking all handlers registered
        for the specific lifecycle event.

        :param event: Lifecycle event to handle
        :return: Nothing
        """
        for handler in self.handlers_for_lifecycle_event(event):
            await handler(event)

    async def on_request(self, request: models.Request) -> models.Response:
        """
        Handler function called for each webhook event.

        This should verify the request originated from GitHub, parse the
        content into the appropriate models and invoke all handlers registered
        for the specific GitHub event/action id.

        :param request: Request to handle
        :return: Response
        """
        # Verify the webhook request; return 401 when invalid.
        self.verify_request(request, self.app_id, self.webhook_secret)

        # Parse request body into event of appropriate type based on event name/action.
        event = self.parse_request(request)

        # Wrap event into Context instance that providers clean interface/helpers to
        # user defined event handler functions.
        context = self.create_context(event, self.app_id, self.private_key)

        # Process all registered event handlers for the current event/context.
        return await self.on_event(context)

    async def on_event(self, context: models.Context) -> models.Response:
        """
        Process the given context for all registered middleware and handlers.

        Middleware functions can optional return a response. If they chose to do so,
        further processing of the request will be stopped and the response will be immediately
        returned to the caller. If no response is returned, execution of the middleware chain
        and handler functions will continue.

        Handler functions can optionally return a response. If they chose to do so,
        the response returned by this function will be prioritized by the greatest status_code
        value. As in, if the first handler returns a 200 OK and the second returns a 500 Server Error,
        this function will return the 500 Server Error.

        If no handler functions return a response, this will default to returning a 200 OK response.

        :param context: Context to pass to all event handlers
        :return: Response based on handlers
        """
        response = models.Response(status_code=200)

        for middleware in self.middleware_for_event(context.event):
            middleware_response = await self.process_middleware(middleware, context)
            if middleware_response:
                return middleware_response

        for handler in self.handlers_for_event(context.event):
            handler_response = await self.process_handler(handler, context)
            if handler_response.status_code >= response.status_code:
                response = handler_response

        return response

    async def process_middleware(self,
                                 middleware: AsyncEventMiddleware,
                                 context: models.Context) -> models.Response:
        """
        Run the given middleware with the given context.

        :param middleware: Middleware to run
        :param context: Context to use
        :return: Response
        """
        try:
            return self.wrap_response(await middleware(context))
        except Exception as ex:
            return models.Response(content=str(ex),
                                   status_code=500)

    async def process_handler(self,
                              handler: AsyncEventHandler,
                              context: models.Context) -> models.Response:
        """
        Run the given handler with the given context.

        If the handler does not return a response, this will default to returning a 200 OK response.

        :param handler: Handler to run
        :param context: Context to use
        :return: Response
        """
        try:
            return self.wrap_response(await handler(context))
        except Exception as ex:
            return models.Response(content=str(ex),
                                   status_code=500)

    def validate_middleware(self, middleware: AsyncEventMiddleware) -> None:
        """
        Validate that the given middleware function is valid for this app.

        If the middleware is not valid, a InvalidEventMiddleware exception is raised.

        :param middleware: Middleware to validate
        :return: Nothing
        """
        if not inspect.iscoroutinefunction(middleware):
            raise errors.InvalidEventMiddleware('Event middleware functions for ASGI apps must be "async"')

    def validate_handler(self, handler: AsyncEventHandler) -> None:
        """
        Validate that the given handler function is valid for this app.

        If the handler is not valid, a InvalidEventHandler exception is raised.

        :param handler: Handler to validate
        :return: Nothing
        """
        if not inspect.iscoroutinefunction(handler):
            raise errors.InvalidEventHandler('Event handler functions for ASGI apps must be "async"')
