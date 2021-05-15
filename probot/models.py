"""
    probot/models
    ~~~~~~~~~~~~~

    Contains commonly used model types.
"""
import enum

from typing import Any, Dict, Generic, List, TypeVar

from pydantic import BaseSettings, BaseModel, Field, ValidationError

from . import defaults, descriptors, errors, github, log

# Alias the 'github' module API for cleaner imports.
new_event = github.new_event
new_id = github.new_id
ID = github.ID
Event = github.Event
ActionT = github.ActionT
Issue = github.Issue
Organization = github.Organization
PullRequest = github.PullRequest
Repository = github.Repository
Github = github.Github
GitBlob = github.GitBlob
GitRef = github.GitRef
GitTree = github.GitTree
Commit = github.Commit
GitCommit = github.GitCommit
GitAuthor = github.GitAuthor
GithubException = github.GithubException
InputGitAuthor = github.InputGitAuthor
InputGitTreeElement = github.InputGitTreeElement

EventName = github.EventName
TargetType = github.TargetType

EventT = TypeVar('EventT', bound=github.Event)


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


class LifecycleEvent(str, enum.Enum):
    """
    Enumeration for all known Probot lifecycle events.
    """
    Startup = 'startup'
    Shutdown = 'shutdown'


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


class Response(BaseModel):
    """
    Represents a framework agnostic HTTP response.
    """
    status_code: int = 200
    content: str = ''
    headers: Any = None


# TypeVar for types that derive from :class:`~probot.models.Response`.
ResponseT = TypeVar('ResponseT', bound=Response)


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

    @property
    def is_bot(self) -> bool:
        """
        Check if event sender is a bot user.
        """
        sender = self.event.payload.get('sender')
        return sender and sender.type == TargetType.Bot

    @descriptors.cached
    def default_branch(self) -> Issue:
        """
        Create a memoized instance of the event repository default branch.
        """
        repo = self.repo
        if not repo:
            return None
        return repo.get_branch(repo.default_branch)

    @descriptors.cached
    def comment(self) -> Issue:
        """
        Create a memoized instance of the event comment.
        """
        comment = self.event.payload.get('comment')
        if not comment:
            return None
        if self.event.id.name == EventName.CommitComment:
            return self.repo.get_comment(comment.id)
        if self.event.id.name == EventName.IssueComment:
            return self.issue.get_comment(comment.id)
        if self.event.id.name == EventName.PullRequestReviewComment:
            return self.pull_request.get_comment(comment.id)
        raise ValueError('Comment for unknown event name {}'.format(self.event.name))

    @descriptors.cached
    def installation(self) -> Issue:
        """
        Create a memoized instance of the event installation.
        """
        installation = self.event.payload.get('installation')
        if not installation:
            return None
        return self.github.get_installation(installation.id)

    @descriptors.cached
    def issue(self) -> Issue:
        """
        Create a memoized instance of the event issue.
        """
        issue = self.event.payload.get('issue')
        if not issue:
            return None
        return self.repo.get_issue(issue.number)

    @descriptors.cached
    def org(self) -> Organization:
        """
        Create memoized instance of the event organization.
        """
        org = self.event.payload.get('organization')
        if not org:
            return self.repo.organization
        return self.github.get_organization(org.login)

    @descriptors.cached
    def pull_request(self) -> Issue:
        """
        Create a memoized instance of the event pull request.
        """
        pr = self.event.payload.get('pull_request')
        if not pr:
            return None
        return self.repo.get_pull(pr.number)

    @descriptors.cached
    def ref(self) -> Issue:
        """
        Create a memoized instance of the event ref.
        """
        ref = self.event.payload.get('ref')
        if not ref:
            return None
        return self.repo.get_git_ref(ref)

    @descriptors.cached
    def repo(self) -> Repository:
        """
        Create memoized instance of the event repository.
        """
        repo = self.event.payload.get('repository')
        if not repo:
            return None
        return self.github.get_repo(repo.id)


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
