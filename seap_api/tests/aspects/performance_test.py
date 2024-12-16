import pytest
import time
from unittest.mock import patch
from functools import wraps
from aspects.performance import cache_result


# Test class with instance and static methods
class ExampleClass:
    @cache_result(ttl_seconds=2)
    def instance_method(self, x, **kwargs):
        return x * 2

    @cache_result(ttl_seconds=2)
    @staticmethod
    def static_method(x):
        return x * 3



@pytest.fixture
def mock_logger():
    """Fixture to mock logger.info."""
    with patch("aspects.performance.logger.info") as mock_info:
        yield mock_info


def test_cache_instance_method(mock_logger):
    instance = ExampleClass()

    # First call - not cached
    result1 = instance.instance_method(5)
    assert result1 == 10
    assert mock_logger.call_count >= 1

    # Second call with same arguments - should be cached
    result2 = instance.instance_method(5)
    assert result2 == 10

    # Check for cache hit in logs
    assert any("Cache hit" in call[0][0] for call in mock_logger.call_args_list)


def test_cache_static_method(mock_logger):
    # First call - not cached
    result1 = ExampleClass.static_method(4)
    assert result1 == 12

    # Second call with same arguments - should be cached
    result2 = ExampleClass.static_method(4)
    assert result2 == 12

    # Check for cache hit in logs
    assert any("Cache hit" in call[0][0] for call in mock_logger.call_args_list)


def test_cache_expiration(mock_logger):
    instance = ExampleClass()

    # First call - not cached
    result1 = instance.instance_method(3)
    assert result1 == 6

    # Wait for cache to expire
    time.sleep(3)

    # Call again after cache expiration
    result2 = instance.instance_method(3)
    assert result2 == 6

    # Check for cache expiration in logs
    assert any("Cache expired" in call[0][0] for call in mock_logger.call_args_list)


def test_cache_different_arguments(mock_logger):
    instance = ExampleClass()

    # Different arguments should result in different results
    result1 = instance.instance_method(2)
    result2 = instance.instance_method(3)
    assert result1 == 4
    assert result2 == 6

    # Check that two different cache entries were created
    assert mock_logger.call_count >= 2
    assert any("No cache entry found" in call[0][0] for call in mock_logger.call_args_list)


def test_cache_key_uniqueness(mock_logger):
    instance = ExampleClass()

    # Use different positional arguments for uniqueness
    result1 = instance.instance_method(4)
    result2 = instance.instance_method(5)  # Different argument

    assert result1 == 8
    assert result2 == 10

    # Check that the logs show two different cache entries created
    assert mock_logger.call_count >= 2
    assert any("No cache entry found" in call[0][0] for call in mock_logger.call_args_list)
