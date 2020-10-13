"""
    probot/models
    ~~~~~~~~~~~~~

    Contains commonly used model types.
"""
from typing import Any, Dict, List, Optional, TypeVar

from pydantic import dataclasses, BaseModel

from . import github

# Alias the 'github' module API for cleaner imports.
new_event = github.new_event
new_id = github.new_id
ID = github.ID
Event = github.Event
EventT = github.EventT


class Request:
    """
    Represents a framework agnostic HTTP request.

    TODO - Add helper methods for translating framework-specific request models
    into this type upon creation.
    """
    def __init__(self,
                 method: str,
                 body_raw: bytes,
                 body_json: Dict[str, Any],
                 query: Dict[str, List[str]] = None,
                 headers: Dict[str, List[str]] = None) -> None:
        self.method = method
        self.body_raw = body_raw
        self.body_json = body_json
        self.query = query
        self.headers = headers


# TypeVar for types that derive from :class:`~probot.models.Request`.
RequestT = TypeVar('RequestT', bound=Request)


@dataclasses.dataclass
class Response:
    """
    Represents a framework agnostic HTTP response.
    """
    status_code: int = 200
    content: str = ''
    headers: Any = None


# TypeVar for types that derive from :class:`~probot.models.Response`.
ResponseT = TypeVar('ResponseT', bound=Response)


class App:
    """
    Represents a framework agnostic HTTP app server.
    """


class Context(BaseModel):
    """
    Contains all context and helpers for handling an individual webhook event.

    TODO: Should this be Generic[T] where T is EventT?
    """
    event: github.EventT
    github: Optional[github.Github]

    @property
    def installation_id(self):
        return getattr(getattr(self.event.payload, 'installation', None), 'id', None)

    class Config:
        arbitrary_types_allowed = True
