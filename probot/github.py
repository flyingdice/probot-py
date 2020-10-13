"""
    probot/github
    ~~~~~~~~~~~~

    Contains all GitHub specific functionality.
"""
from typing import Optional

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


def create_github_installation_api(event: EventT,
                                   app_id: str,
                                   private_key: str) -> Optional[Github]:
    """
    Create a new GitHub installation for the given event that was generated for
    a GitHub App.

    :param event: Event for a GitHub App
    :param app_id: ID of GitHub App we're running
    :param private_key: Private key of the GitHub App we're running
    :return: GitHub instance
    """
    # TODO: Create an GitHub instance that isn't based on installation? OAuth?
    if not event.installation_id:
        return None

    integration = GithubIntegration(app_id, private_key)
    authorization = integration.get_access_token(event.installation_id)
    return Github(authorization.token)
