import pytest
from unittest.mock import patch
from api.scrape.request_strategy import GetRequestStrategy, PostRequestStrategy


@pytest.fixture
def url():
    return "http://example.com/api"


@pytest.fixture
def headers():
    return {"Content-Type": "application/json"}


@pytest.fixture
def body():
    return {"key": "value"}


def test_get_request_strategy(url, headers):
    with patch("scrape.request_strategy.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"message": "success"}

        strategy = GetRequestStrategy()
        response = strategy.make_request(url, headers)

        mock_get.assert_called_once_with(url, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"message": "success"}


def test_post_request_strategy(url, headers, body):
    with patch("scrape.request_strategy.requests.post") as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"message": "created"}

        strategy = PostRequestStrategy()
        response = strategy.make_request(url, headers, body)

        mock_post.assert_called_once_with(
            url,
            headers=headers,
            json=body,
            verify=True
        )

        assert response.status_code == 201
        assert response.json() == {"message": "created"}
