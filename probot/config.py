"""
    probot/config
    ~~~~~~~~~~~~~

    Contains functionality for defining application configuration.
"""
import dataclasses
import functools
import os


def env_var(key: str) -> str:
    return os.environ[f'PROBOT_{key.upper()}']


default_app_id = functools.partial(env_var, 'APP_ID')
default_webhook_secret = functools.partial(env_var, 'WEBHOOK_SECRET')
default_private_key = functools.partial(env_var, 'PRIVATE_KEY')


@dataclasses.dataclass
class Config:
    """
    Defines probot configuration.
    """
    app_id: str = dataclasses.field(default_factory=default_app_id)
    private_key: str = dataclasses.field(default_factory=default_private_key)
    webhook_secret: str = dataclasses.field(default_factory=default_webhook_secret)
