import pytest
import requests_mock

from api.scrape.request_strategy import GetRequestStrategy, PostRequestStrategy


@pytest.fixture
def mock_url():
    return "https://api.example.com/resource"


def test_get_request_strategy(mock_url):
    strategy = GetRequestStrategy()
    with requests_mock.Mocker() as m:
        m.get(mock_url, json={"message": "Success"}, status_code=200)

        response = strategy.make_request(mock_url, headers={"Authorization": "Bearer token"})

        assert response.status_code == 200
        assert response.json() == {"message": "Success"}


def test_post_request_strategy(mock_url):
    strategy = PostRequestStrategy()
    with requests_mock.Mocker() as m:
        m.post(mock_url, json={"message": "Created"}, status_code=201)

        body = {"key": "value"}
        response = strategy.make_request(mock_url, headers={"Authorization": "Bearer token"}, body=body)

        assert response.status_code == 201
        assert response.json() == {"message": "Created"}
        history = m.request_history
        assert len(history) == 1
        assert history[0].json() == body
