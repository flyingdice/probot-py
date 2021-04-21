"""
    probot/github
    ~~~~~~~~~~~~

    Contains all GitHub specific functionality.
"""
import ghwht

from github import (Commit, Github, GithubIntegration, GithubException, GitAuthor,
                    GitCommit, GitRef, GitTree, Issue, Organization, PullRequest, Repository)

# Alias PyGithub API for cleaner imports.
Github = Github
GithubIntegration = GithubIntegration
Issue = Issue
Organization = Organization
PullRequest = PullRequest
Repository = Repository
GitRef = GitRef
GitTree = GitTree
Commit = Commit
GitCommit = GitCommit
GitAuthor = GitAuthor
GithubException = GithubException

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

    integration = GithubIntegration(app_id, private_key)
    authorization = integration.get_access_token(installation_id)
    return Github(authorization.token)
