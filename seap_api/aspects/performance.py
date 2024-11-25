from functools import wraps
import time
import logging
from threading import Lock
import inspect

logger = logging.getLogger(__name__)


def cache_result(ttl_seconds=300):
    """
    Caches function results for a specified time period.
    Compatible with both static and instance methods.
    """
    cache = {}
    cache_lock = Lock()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Handle static methods
            is_static = isinstance(func, staticmethod) or len(inspect.getfullargspec(func).args) == 0
            # For static methods, use all args; for instance methods, skip self
            cache_args = args if is_static else args[1:]
            cache_key = str(cache_args) + str(kwargs)

            with cache_lock:
                if cache_key in cache:
                    result, timestamp = cache[cache_key]
                    if time.time() - timestamp < ttl_seconds:
                        logger.debug(f"Cache hit for {func.__name__}")
                        return result

            result = func(*args, **kwargs)

            with cache_lock:
                cache[cache_key] = (result, time.time())
            return result

        return staticmethod(wrapper) if isinstance(func, staticmethod) else wrapper

    return decorator
