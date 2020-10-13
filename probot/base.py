"""
    probot/base
    ~~~~~~~~~~~

    Contains abstract base types to be extended.
"""
import abc
import collections
import hmac
from typing import Callable, Dict, Generic, List, Optional, Type, TypeVar

from . import config, defaults, errors, github, models
from .hints import AdapterAppT, AdapterRequestT, AdapterResponseT, EventHandlerT


class Adapter(Generic[AdapterAppT, AdapterRequestT, AdapterResponseT],
              metaclass=abc.ABCMeta):
    """
    Abstract adapter for handling HTTP requests/responses.
    """
    methods = [defaults.METHOD]

    def __init__(self,
                 app: AdapterAppT,
                 path: str = defaults.PATH) -> None:
        self.app = app
        self.path = path


# Type alias for :class:`~probot.base.Adapter` derived classes.
AdapterT = TypeVar('AdapterT', bound=Adapter)


class App(Generic[AdapterT, EventHandlerT],
          metaclass=abc.ABCMeta):
    """
    Abstract HTTP application.
    """
    def __init__(self, adapter: AdapterT) -> None:
        self.adapter = adapter
        self.adapter.register(self.on_request)
        self.handlers: Dict[models.ID, List[EventHandlerT]] = collections.defaultdict(list)
        self.app_id = None
        self.private_key = None
        self.webhook_secret = None

    def configure(self, conf: config.Config) -> None:
        """
        Configure this app using probot config.

        :param conf: Config to use
        :return: Nothing
        """
        self.app_id = conf.app_id
        self.private_key = conf.private_key
        self.webhook_secret = conf.webhook_secret

    def register_handler(self,
                         event_id: models.ID,
                         handler: EventHandlerT) -> None:
        """
        Register the user defined event handler function for the given event id.

        If the handler is not valid for this app, a InvalidEventHandler exception is raised.

        :param event_id: Event ID to register the handler for
        :param handler: User defined handler function to run
        :return: Nothing
        """
        self.validate_handler(handler)
        self.handlers[event_id].append(handler)

    @abc.abstractmethod
    def validate_handler(self, handler: EventHandlerT) -> None:
        """
        Validate that the given handler function is valid for this app.

        If the handler is not valid, a InvalidEventHandler exception is raised.

        :param handler: Handler to validate
        :return: Nothing
        """
        raise NotImplementedError('Must be implemented by derived class')

    @abc.abstractmethod
    def on_request(self, request: models.Request) -> models.Response:
        """
        Handler function called for each HTTP request.

        This is responsible for verifying the request, converting the payload
        into the appropriate model types and calling the `on_event` handler.
        content into the appropriate models and invoke all handlers registered
        for the specific GitHub event/action id.

        :param request: Request to handle
        :return: Response
        """
        raise NotImplementedError('Must be implemented by derived class')

    @staticmethod
    def create_context(event: models.EventT,
                       app_id: str,
                       private_key: str) -> models.Context:
        """
        Create context for the given webhook event.

        :param event: Event to create context for
        :param app_id: ID of the GitHub App
        :param private_key: PEM of the GitHub App
        :return: Context
        """
        return models.Context(
            event=event,
            github=github.create_github_installation_api(event, app_id, private_key)
        )

    @staticmethod
    def parse_request(request: models.Request) -> models.EventT:
        """
        Parse the given request into an event.

        :param request: Request to parse
        :return: Event
        """
        delivery_id = request.headers['X-GitHub-Delivery']
        event_name = request.headers['X-GitHub-Event']
        hook_id = int(request.headers['X-GitHub-Hook-ID'])
        payload = request.body_json
        action = payload.pop('action', None)
        return models.new_event(delivery_id, event_name, hook_id, action, payload)

    def verify_request(self,
                       request: models.Request,
                       app_id: str,
                       webhook_secret: str) -> None:
        """
        Verify the given request.

        If unverified, raise an HTTP 401 Unauthorized exception.

        :param request: Request to verify
        :param app_id: Expected GitHub app id
        :param webhook_secret: Shared webhook secret between GitHub and GitHub App
        :return: Nothing
        """
        self.verify_request_signature(request, webhook_secret)
        self.verify_request_target_id(request, app_id)

    @staticmethod
    def verify_request_signature(request: models.Request,
                                 webhook_secret: str) -> None:
        """
        Verify the given request originated from GitHub.

        If unverified, raise an HTTP 401 Unauthorized exception.

        :param request: Request to validate
        :param webhook_secret: Shared webhook secret between GitHub and GitHub App
        :return: Nothing
        """
        algorithm, digest = request.headers['X-Hub-Signature'].split('=')

        obj = hmac.new(
            key=webhook_secret.encode('utf-8'),
            msg=request.body_raw,
            digestmod=algorithm
        )

        match = hmac.compare_digest(digest, obj.hexdigest())
        if not match:
            raise errors.HTTPException(401, 'Invalid webhook signature')

    @staticmethod
    def verify_request_target_id(request: models.Request,
                                 app_id: str) -> None:
        """
        Verify the given request is for the expected GitHub App.

        If unverified, raise an HTTP 401 Unauthorized exception.

        :param request: Request to validate
        :param app_id: Expected GitHub app id
        :return: Nothing
        """
        target_id = request.headers.get('X-GitHub-Hook-Installation-Target-ID')
        if not target_id:
            raise errors.HTTPException(401, 'Missing installation target id')
        if target_id != app_id:
            raise errors.HTTPException(401, 'Installation target id mismatch')

    @staticmethod
    def wrap_response(result: Optional[models.Response]) -> models.Response:
        """
        Wrap the result of a handler execution into a Response object.

        If the handler returned a response, use that.
        If the handler did not return a response, return a 200 OK response.

        :param result: Result of a handler execution
        :return: Response
        """
        return result if result else models.Response(status_code=200)


# Type alias for :class:`~probot.base.App` derived classes.
AppT = TypeVar('AppT', bound=App)


class Probot(Generic[AppT, AdapterT, AdapterAppT],
             metaclass=abc.ABCMeta):
    """
    Abstract probot application.

    This class is responsible for registering user defined webhook event
    handler functions and registering itself with a web framework application.
    """
    app_cls: Optional[Type[AppT]] = None
    adapter_cls: Optional[Type[AdapterT]] = None

    def __init__(self,
                 app: Optional[AdapterAppT] = None,
                 conf: Optional[config.Config] = None) -> None:
        if not self.app_cls:
            raise errors.ConfigurationException('Derived Probot types must define "app_cls"')
        if not self.adapter_cls:
            raise errors.ConfigurationException('Derived Probot types must define "adapter_cls"')

        self.config = conf or config.Config()
        self.app = self.app_cls(self.adapter_cls(app))
        self.app.configure(self.config)

    def on(self, *event_ids: str) -> Callable[[EventHandlerT], EventHandlerT]:
        """
        Register functions to handle specific GitHub events/actions.

        @app.on('issues.created')
        async def on_issue_created(event, context):
            ...

        You also may specify multiple events/actions for a single handler if you desire.

        @app.on('issues.created', 'pull_request.created')
        async def on_item_created(event, context):
            ...

        :param event_ids: Identifiers to map to handler
        :return: Registered event listener function
        """
        def wrapper(handler: EventHandlerT) -> EventHandlerT:
            for event_id in event_ids:
                self.app.register_handler(models.new_id(event_id), handler)
            return handler
        return wrapper


# Type alias for :class:`~probot.base.Probot` derived classes.
ProbotT = TypeVar('ProbotT', bound=Probot)
