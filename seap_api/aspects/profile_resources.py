import logging
from functools import wraps
import time
from statistics import mean, stdev

import psutil

logger = logging.getLogger(__name__)

# Variabile globale pentru monitorizare
execution_times = {}


def profile_resources(func):
    """
    Profiler pentru timpul de execuție și utilizarea resurselor.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        process = psutil.Process()
        memory_before = process.memory_info().rss

        try:
            result = func(*args, **kwargs)
        finally:
            memory_after = process.memory_info().rss
            duration = time.time() - start_time
            logger.info(
                f"{func.__name__} - Durată: {duration:.4f}s, "
                f"Memorie utilizată: {(memory_after - memory_before) / 1024:.2f} KB"
            )
        return result

    return wrapper

