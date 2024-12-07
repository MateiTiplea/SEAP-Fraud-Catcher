import logging
import os
from datetime import datetime
from functools import wraps
from logging import FileHandler, Formatter

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create logs directory
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Create file handler with daily rotation
log_file = os.path.join(
    logs_dir, f'error_handler_{datetime.now().strftime("%Y%m%d")}.log'
)
handler = FileHandler(log_file)
handler.setLevel(logging.INFO)

# Create formatter
formatter = Formatter(
    "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
logger.addHandler(handler)


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
                # Get method name
                if hasattr(func, "__qualname__"):
                    method_name = func.__qualname__
                else:
                    method_name = func.__name__

                # Get instance name for class methods
                instance_name = args[0].__class__.__name__ if args else None

                # Build detailed error message
                error_msg = f"Error in {instance_name + '.' if instance_name else ''}{method_name}: {str(e)}\n"
                error_msg += f"Args: {args[1:] if instance_name else args}\n"  # Skip self for instance methods
                error_msg += f"Kwargs: {kwargs}\n"

                # For HTTPError, add response details if available
                if hasattr(e, "response"):
                    try:
                        error_msg += f"Response body: {e.response.text}\n"
                        error_msg += f"Request URL: {e.response.url}\n"
                        error_msg += f"Request headers: {e.response.request.headers}\n"
                        error_msg += f"Request body: {e.response.request.body}\n"
                    except:
                        pass

                logger.error(error_msg)
                if reraise:
                    raise
                return None

        return staticmethod(wrapper) if isinstance(func, staticmethod) else wrapper

    return decorator
