"""
    probot/apps/wsgi
    ~~~~~~~~~~~~~~~~

    Contains HTTP application for use with WSGI (sync) adapters.
"""
import inspect

from .. import base, errors, models
from ..hints import SyncEventHandler
from . import adapter


class App(base.App[adapter.WSGIAdapterT, SyncEventHandler]):
    """
    App for WSGI (sync) adapters.
    """
    def on_request(self, request: models.Request) -> models.Response:
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
        return self.on_event(context)

    def on_event(self, context: models.Context) -> models.Response:
        """
        Process the given context for all registered handlers.

        Handler functions can optionally return a response. If they chose to do so,
        the response returned by this function will be prioritized by the greatest status_code
        value. As in, if the first handler returns a 200 OK and the second returns a 500 Server Error,
        this function will return the 500 Server Error.

        If no handler functions return a response, this will default to returning a 200 OK response.

        :param context: Context to pass to all event handlers
        :return: Response based on handlers
        """
        response = models.Response(status_code=200)

        for handler in self.handlers[context.event.id]:
            handler_response = self.process_handler(handler, context)
            if handler_response.status_code > response.status_code:
                response = handler_response

        return response

    def process_handler(self,
                        handler: SyncEventHandler,
                        context: models.Context) -> models.Response:
        """
        Run the given handler with the given context.

        If the handler does not return a response, this will default to returning a 200 OK response.

        :param handler: Handler to run
        :param context: Context to use
        :return: Response
        """
        try:
            return self.wrap_response(handler(context))
        except Exception as ex:
            response = models.Response(content=str(ex),
                                       status_code=500)
        return response

    def validate_handler(self, handler: SyncEventHandler) -> None:
        """
        Validate that the given handler function is valid for this app.

        If the handler is not valid, a InvalidEventHandler exception is raised.

        :param handler: Handler to validate
        :return: Nothing
        """
        if inspect.iscoroutinefunction(handler):
            raise errors.InvalidEventHandler('Event handler functions for WSGI apps must not be "async"')
