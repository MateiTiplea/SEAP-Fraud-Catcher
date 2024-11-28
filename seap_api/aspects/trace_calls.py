import logging
from functools import wraps

logger = logging.getLogger(__name__)

call_graph = {}


def trace_calls(func):
    """
    Monitorizează și înregistrează dependențele funcționale.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        parent = trace_calls.current_function
        trace_calls.current_function = func.__name__
        if parent:
            call_graph.setdefault(parent, []).append(func.__name__)
            logging.info(f"{parent} -> {func.__name__}")  # Debug output
        else:
            logging.info(f"{func.__name__} (entry point)")  # Entry point of the call graph
        try:
            return func(*args, **kwargs)
        finally:
            trace_calls.current_function = parent

    return wrapper


trace_calls.current_function = None
