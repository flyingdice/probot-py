"""
    probot/log
    ~~~~~~~~~~

    Contains functionality for logging.
"""
import logging

LOG = logging.getLogger(__package__)


def get_logger(name):
    return LOG.getChild(name)
