"""
    probot/api/api
    ~~~~~~~~~~~~~~

    Defines the public API for the `probot` package.
"""
from .. import errors, github, hints, models

#: Defines the '__all__' for the API.
ALL = [
    'Context',
    'Event',
    'EventHandlerResponse',
    'HTTPException',
    'ID',
    'InvalidEventHandler',
    'Probot',
    'ProbotException',
    'Repository',
    'Request',
    'Response',
    'Settings',
    'CheckRunContext',
    'CheckSuiteContext',
    'CreateContext',
    'DeleteContext',
    'ForkContext',
    'InstallationContext',
    'InstallationRepositoriesContext',
    'LabelContext',
    'PingContext',
    'PublicContext',
    'PullRequestContext',
    'PushContext',
    'ReleaseContext',
    'RepositoryContext'
]


# Alias common imports so framework specific packages can access them.
Context = models.Context
Event = models.Event
EventHandlerResponse = hints.EventHandlerResponse
HTTPException = errors.HTTPException
ID = models.ID
InvalidEventHandler = errors.InvalidEventHandler
ProbotException = errors.ProbotException
Repository = models.Repository
Request = models.Request
Response = models.Response
Settings = models.Settings

CheckRunContext = models.Context[github.CheckRunEvent]
CheckSuiteContext = models.Context[github.CheckSuiteEvent]
CreateContext = models.Context[github.CreateEvent]
DeleteContext = models.Context[github.DeleteEvent]
ForkContext = models.Context[github.ForkEvent]
InstallationContext = models.Context[github.InstallationEvent]
InstallationRepositoriesContext = models.Context[github.InstallationRepositoriesEvent]
LabelContext = models.Context[github.LabelEvent]
PingContext = models.Context[github.PingEvent]
PublicContext = models.Context[github.PublicEvent]
PullRequestContext = models.Context[github.PullRequestEvent]
PushContext = models.Context[github.PushEvent]
ReleaseContext = models.Context[github.ReleaseEvent]
RepositoryContext = models.Context[github.RepositoryEvent]
