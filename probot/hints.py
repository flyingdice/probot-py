"""
    probot/hints
    ~~~~~~~~~~~~

    Contains type hints used across the package.
"""
from typing import Awaitable, Callable, Optional, TypeVar

from . import models

AdapterT = TypeVar('AdapterT')
AdapterAppT = TypeVar('AdapterAppT')
AdapterRequestT = TypeVar('AdapterRequestT')
AdapterResponseT = TypeVar('AdapterResponseT')


# Type alias for the return value of user defined handler functions.
EventHandlerResponse = Optional[models.Response]

# Type definition for async user defined handler functions on a probot app that
# takes context objects and returns optional responses.
AsyncEventHandler = Callable[[models.Context], Awaitable[EventHandlerResponse]]

# # Type definition for a async registered user defined handler function
# # for webhook events.
# RegisteredAsyncEventHandler = Callable[[AsyncEventHandler], AsyncEventHandler]

# Type definition for sync user defined handler functions on a probot app that
# takes context objects and returns optional responses.
SyncEventHandler = Callable[[models.Context], EventHandlerResponse]

# Type definition for async or sync event handlers.
EventHandlerT = TypeVar('EventHandlerT', AsyncEventHandler, SyncEventHandler)

# Type definition for a sync registered user defined handler function
# for webhook events.
RegisteredEventHandler = Callable[[EventHandlerT], EventHandlerT]

# Type definition for async handler functions that take probot requests
# and return probot response objects.
ProbotAsyncHandler = Callable[[models.Request], Awaitable[models.Response]]

# Type definition for async adapter handler functions that wrap native handlers
# and handle adapter specific request/response objects.
AdapterAsyncHandler = Callable[[AdapterRequestT], Awaitable[AdapterResponseT]]

# Type definition for sync handler functions that take probot requests
# and return probot response objects.
ProbotSyncHandler = Callable[[models.Request], models.Response]

# Type definition for sync adapter handler functions that wrap native handlers
# and handle adapter specific request/response objects.
AdapterSyncHandler = Callable[[AdapterRequestT], AdapterResponseT]
