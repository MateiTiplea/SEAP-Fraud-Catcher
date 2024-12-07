from functools import wraps
import logging
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


def handle_exceptions(error_types=(Exception,), num_retries=3, reraise=True):
    def decorator(func):
        @retry(
            stop=stop_after_attempt(num_retries),
            wait=wait_exponential(min=1, max=10),
            retry=retry_if_exception_type(error_types),
            reraise=reraise,
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                if hasattr(func, '__qualname__'):
                    method_name = func.__qualname__
                else:
                    method_name = func.__name__

                logger.error(f"Error in {method_name}: {str(e)}")
                if reraise:
                    raise
                return None

        return staticmethod(wrapper) if isinstance(func, staticmethod) else wrapper

    return decorator
