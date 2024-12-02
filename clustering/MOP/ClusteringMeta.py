from abc import ABCMeta
import time
from types import FunctionType
import os


def log_to_file(message, filename="log.txt"):
    log_dir = os.path.dirname(filename)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    with open(filename, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


def format_args(args, kwargs):

    formatted_args = ", ".join(str(arg) if not hasattr(arg, '__dict__') else repr(arg.__dict__) for arg in args)
    formatted_kwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    return f"{formatted_args}" + (f", {formatted_kwargs}" if kwargs else "")


def monitor_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()

        # Formatare parametri
        formatted_args = format_args(args[1:], kwargs)

        log_to_file(f"Se execută {func.__name__} cu parametrii: {formatted_args}")
        result = func(*args, **kwargs)
        end_time = time.time()

        formatted_result = result if isinstance(result, (str, int, float, list, dict, tuple)) else repr(result)
        log_to_file(f"Rezultat {func.__name__}: {formatted_result}")
        log_to_file(f"Timp execuție {func.__name__}: {end_time - start_time:.4f} secunde")
        return result

    return wrapper


class ClusteringMeta(ABCMeta):
    def __new__(cls, name, bases, dct):
        for attr_name, attr_value in dct.items():
            if isinstance(attr_value, FunctionType) and not attr_name.startswith("__"):
                dct[attr_name] = monitor_function(attr_value)
        return super().__new__(cls, name, bases, dct)

