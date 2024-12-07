import logging
import time

import psutil

logger = logging.getLogger(__name__)

execution_times = {}


def profile_resources(func):
    """
    Profiler for execution time and resource usage.
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
                f"{func.__name__} - Duration: {duration:.4f}s, "
                f"Used memory: {(memory_after - memory_before) / 1024:.2f} KB"
            )
        return result

    return wrapper
