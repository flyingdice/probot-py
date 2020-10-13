"""
    probot/adapters/base
    ~~~~~~~~~~~~~~~~~~~~

    Contains base types to be used/extended by adapters.
"""
import abc
from typing import Generic, TypeVar

from .. import defaults
from ..hints import AppT, RequestT, ResponseT


class Adapter(Generic[AppT, RequestT, ResponseT],
              metaclass=abc.ABCMeta):
    """
    Abstract adapter for handling HTTP requests/responses.
    """
    methods = [defaults.METHOD]

    def __init__(self,
                 app: AppT,
                 path: str = defaults.PATH) -> None:
        self.app = app
        self.path = path


AdapterT = TypeVar('AdapterT', bound=Adapter)
