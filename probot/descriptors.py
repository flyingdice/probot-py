"""
    probot/descriptors
    ~~~~~~~~~~~~~~~~~~

    Contains descriptors used across the package.
"""
import functools

__all__ = ['cached']


class CachedProperty:
    """
    Descriptor that caches the result of a decorated function.
    """

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


cached = CachedProperty
