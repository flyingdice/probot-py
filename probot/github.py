"""
    probot/github
    ~~~~~~~~~~~~~

    Contains all GitHub specific functionality.
"""
import ghwht

from github import (Commit, Github, GithubIntegration, GithubException, GitAuthor, GitBlob, GitCommit, GitRef,
                    GitTree, InputGitAuthor, InputGitTreeElement, Issue, Organization, PullRequest, Repository)

from . import log

LOG = log.get_logger(__name__)

# Alias PyGithub API for cleaner imports.
Github = Github
GithubIntegration = GithubIntegration
Issue = Issue.Issue
Organization = Organization.Organization
PullRequest = PullRequest.PullRequest
Repository = Repository.Repository
GitBlob = GitBlob.GitBlob
GitRef = GitRef.GitRef
GitTree = GitTree.GitTree
Commit = Commit.Commit
GitCommit = GitCommit.GitCommit
GitAuthor = GitAuthor.GitAuthor
GithubException = GithubException
InputGitAuthor = InputGitAuthor
InputGitTreeElement = InputGitTreeElement

# Alias the ghwht API for cleaner imports.
new_event = ghwht.new_event
new_id = ghwht.new_id
ID = ghwht.ID
Event = ghwht.Event
EventT = ghwht.EventT
ActionT = ghwht.ActionT

EventName = ghwht.EventName
TargetType = ghwht.TargetType

CheckRunEvent = ghwht.CheckRunEvent
CheckSuiteEvent = ghwht.CheckSuiteEvent
CodeScanningAlertEvent = ghwht.CodeScanningAlertEvent
CommitCommentEvent = ghwht.CommitCommentEvent
ContentReferenceEvent = ghwht.ContentReferenceEvent
CreateEvent = ghwht.CreateEvent
DeleteEvent = ghwht.DeleteEvent
DeployKeyEvent = ghwht.DeployKeyEvent
DeploymentEvent = ghwht.DeploymentEvent
DeploymentStatusEvent = ghwht.DeploymentStatusEvent
ForkEvent = ghwht.ForkEvent
GitHubAppAuthorizationEvent = ghwht.GitHubAppAuthorizationEvent
InstallationEvent = ghwht.InstallationEvent
InstallationRepositoriesEvent = ghwht.InstallationRepositoriesEvent
IssueCommentEvent = ghwht.IssueCommentEvent
IssuesEvent = ghwht.IssuesEvent
LabelEvent = ghwht.LabelEvent
MarketplacePurchaseEvent = ghwht.MarketplacePurchaseEvent
MemberEvent = ghwht.MemberEvent
MembershipEvent = ghwht.MembershipEvent
MetaEvent = ghwht.MetaEvent
MilestoneEvent = ghwht.MilestoneEvent
OrganizationEvent = ghwht.OrganizationEvent
PingEvent = ghwht.PingEvent
PublicEvent = ghwht.PublicEvent
PullRequestEvent = ghwht.PullRequestEvent
PushEvent = ghwht.PushEvent
ReleaseEvent = ghwht.ReleaseEvent
RepositoryEvent = ghwht.RepositoryEvent


def create_github_api(event: EventT,
                      app_id: str,
                      private_key: str) -> Github:
    """
    Create a new GitHub client for the given event.

    If the event doesn't contain installation information (for a GitHub App), or
    the event indicates the app access has been revoked, an unauthenticated client is returned.

    :param event: Event for a GitHub App
    :param app_id: ID of GitHub App we're running
    :param private_key: Private key of the GitHub App we're running
    :return: GitHub instance
    """
    installation_id = event.payload.get('installation.id')

    if not installation_id or ghwht.is_access_revoked(event):
        return Github()

    try:
        integration = GithubIntegration(app_id, private_key)
        authorization = integration.get_access_token(installation_id)
    except GithubException as ex:
        if ex.status not in (403, 404):
            raise ex

        LOG.warning('Installation %s no longer has access to app %s',
                    installation_id,
                    app_id)
        return Github()
    else:
        return Github(authorization.token)
