"""
    probot/github
    ~~~~~~~~~~~~

    Contains all GitHub specific functionality.
"""
import ghwht
from github import Github, GithubIntegration

# Alias the ghwht API for cleaner imports.
new_event = ghwht.new_event
new_id = ghwht.new_id
ID = ghwht.ID
Event = ghwht.Event
EventT = ghwht.EventT

# Alias PyGithub API for cleaner imports.
Github = Github
GithubIntegration = GithubIntegration


def create_github_api(event: EventT,
                      app_id: str,
                      private_key: str) -> Github:
    """
    Create a new GitHub client for the given event.

    If the event doesn't contain installation information (for a GitHub App),
    an unauthenticated client is returned.

    :param event: Event for a GitHub App
    :param app_id: ID of GitHub App we're running
    :param private_key: Private key of the GitHub App we're running
    :return: GitHub instance
    """
    installation_id = getattr(getattr(event.payload, 'installation', None), 'id', None)

    if not installation_id:
        return Github()

    integration = GithubIntegration(app_id, private_key)
    authorization = integration.get_access_token(installation_id)
    return Github(authorization.token)
