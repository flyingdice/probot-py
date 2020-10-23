"""
    probot/models
    ~~~~~~~~~~~~~

    Contains commonly used model types.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseSettings, Field, ValidationError, dataclasses, generics

from . import defaults, descriptors, errors, github, log

# Alias the 'github' module API for cleaner imports.
new_event = github.new_event
new_id = github.new_id
ID = github.ID
Event = github.Event
Repository = github.Repository

EventT = TypeVar('EventT', bound=github.Event)


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


class Settings(BaseSettings):
    """
    Contains probot settings.
    """
    app_id: str
    private_key: str
    webhook_secret: str

    webhook_path: str = Field(default=defaults.PATH)

    class Config:
        env_file = defaults.ENV_FILE
        env_prefix = defaults.ENV_PREFIX


def load_settings(env_file: str = defaults.ENV_FILE) -> Settings:
    """
    Load probot settings.

    If the settings failed to load or required values are missing,
    a SettingsException is raised.

    :param env_file: Path to .env file to load
    :return: Settings
    """
    try:
        return Settings(_env_file=env_file)
    except ValidationError as ex:
        raise errors.SettingsException(str(ex)) from ex


class Context(Generic[EventT]):
    """
    Contains all context and helpers for handling an individual webhook event.
    """
    def __init__(self,
                 event: EventT,
                 github: github.Github) -> None:
        self.event = event
        self.github = github
        self.log = log.get_logger(str(event.id))

    @descriptors.cached
    def repo(self) -> Repository:
        """
        Create memoized instance of Repository.
        """
        repo_id = self.event.payload.repository.id
        return self.github.get_repo(repo_id, lazy=True)


CheckRunContext = Context[github.CheckRunEvent]
CheckSuiteContext = Context[github.CheckSuiteEvent]
CodeScanningAlertContext = Context[github.CodeScanningAlertEvent]
CommitCommentContext = Context[github.CommitCommentEvent]
ContentReferenceContext = Context[github.ContentReferenceEvent]
CreateContext = Context[github.CreateEvent]
DeleteContext = Context[github.DeleteEvent]
DeployKeyContext = Context[github.DeployKeyEvent]
DeploymentContext = Context[github.DeploymentEvent]
DeploymentStatusContext = Context[github.DeploymentStatusEvent]
ForkContext = Context[github.ForkEvent]
GitHubAppAuthorizationContext = Context[github.GitHubAppAuthorizationEvent]
InstallationContext = Context[github.InstallationEvent]
InstallationRepositoriesContext = Context[github.InstallationRepositoriesEvent]
IssueCommentContext = Context[github.IssueCommentEvent]
IssuesContext = Context[github.IssuesEvent]
LabelContext = Context[github.LabelEvent]
MarketplacePurchaseContext = Context[github.MarketplacePurchaseEvent]
MemberContext = Context[github.MemberEvent]
MembershipContext = Context[github.MembershipEvent]
MetaContext = Context[github.MetaEvent]
MilestoneContext = Context[github.MilestoneEvent]
OrganizationContext = Context[github.OrganizationEvent]
PingContext = Context[github.PingEvent]
PublicContext = Context[github.PublicEvent]
PullRequestContext = Context[github.PullRequestEvent]
PushContext = Context[github.PushEvent]
ReleaseContext = Context[github.ReleaseEvent]
RepositoryContext = Context[github.RepositoryEvent]

ContextT = TypeVar('ContextT', bound=Context)
