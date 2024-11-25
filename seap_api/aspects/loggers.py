from functools import wraps
import logging
from datetime import datetime
import inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_method_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()

        is_static = isinstance(func, staticmethod) or len(inspect.getfullargspec(func).args) == 0

        # Get class name differently for static vs instance methods
        if is_static:
            class_name = func.__qualname__.split('.')[0] if '.' in func.__qualname__ else ''
        else:
            class_name = args[0].__class__.__name__ if args else ""

        method_name = func.__name__

        logger.info(f"Entering {class_name}.{method_name} at {start_time}")

        log_args = args if is_static else args[1:]
        logger.info(f"Arguments: args={log_args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Successfully completed {class_name}.{method_name} in {duration}s")
            return result
        except Exception as e:
            logger.error(f"Error in {class_name}.{method_name}: {str(e)}")
            raise

    return staticmethod(wrapper) if isinstance(func, staticmethod) else wrapper
