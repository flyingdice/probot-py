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

# Type alias for the return value of user defined middleware functions.
EventMiddlewareResponse = Optional[models.Response]

# Type definition for async user defined middleware functions on a probot app that
# takes context objects, middleware chains, and returns optional responses.
AsyncEventMiddleware = Callable[[models.Context], Awaitable[EventMiddlewareResponse]]

# Type definition for sync user defined middleware functions on a probot app that
# takes context objects, middleware chains, and returns optional responses.
SyncEventMiddleware = Callable[[models.Context], EventMiddlewareResponse]

# Type definition for async or sync event middleware.
EventMiddlewareT = TypeVar('EventMiddlewareT', AsyncEventMiddleware, SyncEventMiddleware)

# Type alias for the return value of user defined lifecycle event functions.
LifecycleEventHandlerResponse = None

# Type definition for async user defined lifecycle event functions on a probot app that
# takes no parameters and returns nothing.
AsyncLifecycleEventHandler = Callable[[models.LifecycleEvent], Awaitable[LifecycleEventHandlerResponse]]

# Type definition for sync user defined lifecycle event functions on a probot app that
# takes no parameters and returns nothing.
SyncLifecycleEventHandler = Callable[[models.LifecycleEvent], LifecycleEventHandlerResponse]

# Type definition for async or sync lifecycle event functions.
LifecycleEventHandlerT = TypeVar('LifecycleEventHandlerT', AsyncLifecycleEventHandler, SyncLifecycleEventHandler)

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

# Type definition for async lifecycle event handler functions that wrap native handlers
# and handle adapter specific request/response objects.
ProbotAsyncLifecycleEventHandler = Callable[[models.LifecycleEvent], Awaitable[LifecycleEventHandlerResponse]]

# Type definition for sync lifecycle event handler functions that wrap native handlers
# and handle adapter specific request/response objects.
ProbotSyncLifecycleEventHandler = Callable[[models.LifecycleEvent], LifecycleEventHandlerResponse]
