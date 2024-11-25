from functools import wraps
from typing import get_type_hints
import logging
import inspect

logger = logging.getLogger(__name__)


def validate_types(func):
    """
    Validates function argument types based on type hints.
    Compatible with both static and instance methods.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        hints = get_type_hints(func)

        # Determine if this is a static method
        is_static = isinstance(func, staticmethod) or len(inspect.getfullargspec(func).args) == 0

        # For instance methods, skip the first argument (self)
        validation_args = args if is_static else args[1:]

        # Get argument names from the function signature
        sig = inspect.signature(func.__wrapped__ if isinstance(func, staticmethod) else func)
        param_names = list(sig.parameters.keys())

        # Validate positional arguments
        for i, value in enumerate(validation_args):
            param_name = param_names[i if is_static else i + 1]
            if param_name in hints:
                expected_type = hints[param_name]
                if not isinstance(value, expected_type):
                    raise TypeError(f"Argument {param_name} must be of type {expected_type}")

        # Validate keyword arguments
        for name, value in kwargs.items():
            if name in hints and not isinstance(value, hints[name]):
                raise TypeError(f"Argument {name} must be of type {hints[name]}")

        return func(*args, **kwargs)

    return staticmethod(wrapper) if isinstance(func, staticmethod) else wrapper