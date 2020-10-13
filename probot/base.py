"""
    probot/adapters/base
    ~~~~~~~~~~~~~~~~~~~~

    Contains abstract base types to be extended.
"""
import abc
import collections
from typing import Callable, Dict, Generic, List, Optional, Type, TypeVar

from . import config, errors, defaults, models
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
        self.webhook_secret = None

    def configure(self, conf: config.Config) -> None:
        """
        Configure this app using probot config.

        :param conf: Config to use
        :return: Nothing
        """
        self.app_id = conf.app_id
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
