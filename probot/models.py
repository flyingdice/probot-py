"""
    probot/models
    ~~~~~~~~~~~~~

    Contains commonly used model types.
"""
from typing import Any, Dict, List, Optional, TypeVar

from pydantic import BaseSettings, BaseModel, Field, dataclasses

from . import defaults, github

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


class Context(BaseModel):
    """
    Contains all context and helpers for handling an individual webhook event.

    TODO: Should this be Generic[T] where T is EventT?
    """
    event: github.EventT
    github: Optional[github.Github]

    class Config:
        arbitrary_types_allowed = True


class Settings(BaseSettings):
    """
    Contains probot settings.
    """
    app_id: str
    private_key: str
    webhook_secret: str

    webhook_path: str = Field(default=defaults.PATH)

    class Config:
        env_file = '.env'
        env_prefix = 'PROBOT_'
