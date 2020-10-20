"""
    probot/errors
    ~~~~~~~~~~~~~

    Contains all exceptions raised by the probot package.
"""
import http


class ProbotException(Exception):
    """
    Base class for all probot exceptions.
    """


class HTTPException(Exception):
    """
    Base class for all probot HTTP related exceptions.
    """
    def __init__(self,
                 status_code: int,
                 detail: str = None) -> None:
        if detail is None:
            detail = http.HTTPStatus(status_code).phrase
        self.status_code = status_code
        self.detail = detail

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"


class InvalidEventHandler(ProbotException):
    """
    Exception raised when a user registered event handler function is invalid.
    """


class SettingsException(ProbotException):
    """
    Base class for all settings related exceptions.
    """


class ConfigurationValueMissing(ProbotException):
    """
    Exception raised when a required configuration value is missing.
    """
    template = 'Missing required configuration value: "{}"'

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(self.template.format(self.name))
