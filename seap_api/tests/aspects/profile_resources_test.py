import pytest
import time
from unittest.mock import patch
from aspects.profile_resources import profile_resources


# Example class using the decorator
class ExampleClass:
    @profile_resources
    def fast_method(self):
        return "fast_result"

    @profile_resources
    def slow_method(self):
        time.sleep(1)
        return "slow_result"


@pytest.fixture
def mock_logger():
    """Fixture to mock logger.info."""
    with patch("aspects.profile_resources.logger.info") as mock_info:
        yield mock_info


def test_profile_fast_method(mock_logger):
    instance = ExampleClass()

    result = instance.fast_method()
    assert result == "fast_result"

    # Ensure logging was called
    mock_logger.assert_called_once()

    log_message = mock_logger.call_args[0][0]
    assert "fast_method" in log_message
    assert "Duration" in log_message
    assert "Used memory" in log_message


def test_profile_slow_method(mock_logger):
    instance = ExampleClass()

    result = instance.slow_method()
    assert result == "slow_result"

    # Ensure logging was called
    mock_logger.assert_called_once()

    log_message = mock_logger.call_args[0][0]
    assert "slow_method" in log_message
    assert "Duration" in log_message
    assert "Used memory" in log_message


def test_profile_free_function(mock_logger):
    @profile_resources
    def sample_function(x):
        time.sleep(0.5)
        return x * 2

    result = sample_function(5)
    assert result == 10

    # Ensure logging was called
    mock_logger.assert_called_once()

    log_message = mock_logger.call_args[0][0]
    assert "sample_function" in log_message
    assert "Duration" in log_message
    assert "Used memory" in log_message
