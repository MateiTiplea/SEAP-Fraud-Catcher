import pytest
from unittest.mock import patch
from aspects.trace_calls import trace_calls, call_graph


# Example class and functions
class ExampleClass:
    @trace_calls
    def method_a(self):
        return self.method_b()

    @trace_calls
    def method_b(self):
        return "result"


@pytest.fixture
def mock_logger():
    """Fixture to mock logger.info."""
    with patch("aspects.trace_calls.logger.info") as mock_info:
        yield mock_info


def test_trace_single_call(mock_logger):
    instance = ExampleClass()

    result = instance.method_a()
    assert result == "result"

    # Ensure logs were generated
    assert mock_logger.call_count >= 2
    assert any("method_a" in call[0][0] for call in mock_logger.call_args_list)
    assert any("method_b" in call[0][0] for call in mock_logger.call_args_list)


def test_call_graph_update(mock_logger):
    instance = ExampleClass()
    call_graph.clear()  # Clear the call graph before testing

    instance.method_a()

    # Verify that the call graph was updated
    assert "aspects.trace_calls.method_a" in call_graph
    assert "method_b" in call_graph["aspects.trace_calls.method_a"]


def test_trace_nested_calls(mock_logger):
    @trace_calls
    def func_a():
        return func_b()

    @trace_calls
    def func_b():
        return "nested_result"

    result = func_a()
    assert result == "nested_result"

    # Ensure logs were generated
    assert mock_logger.call_count >= 2
    assert any("func_a" in call[0][0] for call in mock_logger.call_args_list)
    assert any("func_b" in call[0][0] for call in mock_logger.call_args_list)


def test_entry_point_log(mock_logger):
    @trace_calls
    def entry_point():
        pass

    entry_point()

    # Ensure entry point log was generated
    assert any("entry point" in call[0][0] for call in mock_logger.call_args_list)
