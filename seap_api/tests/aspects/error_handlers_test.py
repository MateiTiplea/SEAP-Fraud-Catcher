import pytest
import re
from unittest.mock import MagicMock, patch
from aspects.error_handlers import handle_exceptions, logger


@pytest.fixture
def mock_logger():
    """Fixture to mock logger.error."""
    with patch.object(logger, "error") as mock_error:
        yield mock_error


def assert_log_contains(mock_logger, pattern):
    """Helper function to match log messages with regex."""
    log_message = mock_logger.call_args[0][0]
    assert re.search(pattern, log_message), f"Log message did not match pattern: {pattern}"


def test_handle_exceptions_retries_and_logs(mock_logger):
    class ExampleClass:
        @handle_exceptions(num_retries=3, error_types=(ValueError,))
        def failing_method(self, arg):
            if arg == "fail":
                raise ValueError("Test failure")

    instance = ExampleClass()

    # The method should fail after retries
    with pytest.raises(ValueError, match="Test failure"):
        instance.failing_method("fail")

    # Assert the method retried 3 times
    assert mock_logger.call_count == 3

    # Check the log message using regex
    assert_log_contains(mock_logger, r"Error in .*ExampleClass\.failing_method.*Test failure")
    assert_log_contains(mock_logger, r"Args: \('fail',\)")
    assert_log_contains(mock_logger, r"Kwargs: \{\}")


def test_handle_exceptions_regular_function(mock_logger):
    @handle_exceptions(num_retries=1, error_types=(IndexError,))
    def failing_function():
        raise IndexError("Function failure")

    # The function should fail after 1 retry
    with pytest.raises(IndexError, match="Function failure"):
        failing_function()

    # Assert the function retried once
    assert mock_logger.call_count == 1

    # Check the log message using regex
    assert_log_contains(mock_logger, r"Error in .*failing_function.*Function failure")


def test_handle_exceptions_static_method(mock_logger):
    class ExampleClass:
        @handle_exceptions(num_retries=2, error_types=(ValueError,))
        @staticmethod
        def failing_static_method():
            raise ValueError("Static method failure")

    # The static method should fail after retries
    with pytest.raises(ValueError, match="Static method failure"):
        ExampleClass.failing_static_method()

    # Assert the static method retried twice
    assert mock_logger.call_count == 2

    # Check the log message using regex
    assert_log_contains(mock_logger, r"Error in .*ExampleClass\.failing_static_method.*Static method failure")


def test_handle_exceptions_logs_response(mock_logger):
    class ExampleClass:
        @handle_exceptions(num_retries=1, error_types=(Exception,))
        def method_with_response(self):
            class CustomException(Exception):
                def __init__(self):
                    self.response = MagicMock()
                    self.response.text = "Response text"
                    self.response.url = "http://example.com"
                    self.response.request.headers = {"Header": "Value"}
                    self.response.request.body = "Request body"
                    super().__init__("Custom exception message")

            raise CustomException()

    instance = ExampleClass()

    # The method should fail after 1 retry
    with pytest.raises(Exception):
        instance.method_with_response()

    # Assert the error message contains response details
    assert_log_contains(mock_logger, r"Response body: Response text")
    assert_log_contains(mock_logger, r"Request URL: http://example.com")
    assert_log_contains(mock_logger, r"Request headers: \{'Header': 'Value'\}")
    assert_log_contains(mock_logger, r"Request body: Request body")
