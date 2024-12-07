import logging
import inspect
from functools import wraps

logger = logging.getLogger(__name__)

call_graph = {}

def trace_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        stack = inspect.stack()
        caller_function_name = "Unknown Function"
        caller_module_name = "Unknown Module"

        for frame_info in stack[2:]:
            module = inspect.getmodule(frame_info.frame)
            caller_function_name = frame_info.function
            if module:
                caller_module_name = module.__name__
                if caller_function_name != func.__name__ or module.__name__ != __name__:
                    break

        logger.info(f"Function '{func.__name__}' in module '{__name__}' was called by "
                    f"'{caller_function_name}' in module '{caller_module_name}'.")

        parent = trace_calls.current_function
        trace_calls.current_function = func.__name__

        if parent:
            call_graph.setdefault(f"{caller_module_name}.{parent}", []).append(func.__name__)
            logger.info(f"{caller_module_name}.{parent} -> {func.__name__}")
        else:
            logger.info(f"{caller_module_name}.{func.__name__} (entry point)")

        try:
            return func(*args, **kwargs)
        finally:
            trace_calls.current_function = parent

    return wrapper

trace_calls.current_function = None