import pytest
import requests_mock
from datetime import datetime

from api.scrape.acquisition_fetcher import AcquisitionFetcher, get_body


@pytest.fixture
def acquisition_fetcher():
    """Fixture for creating an instance of AcquisitionFetcher."""
    return AcquisitionFetcher()


def test_get_body():
    """Test get_body function to ensure it generates the correct payload."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 2)
    body = get_body(start_date, end_date, page_index=1, page_size=100)

    expected_body = {
        "pageSize": 100,
        "showOngoingDa": False,
        "pageIndex": 1,
        "finalizationDateStart": "2024-01-01",
        "finalizationDateEnd": "2024-01-02",
    }

    assert body == '{"pageSize":100,"showOngoingDa":false,"pageIndex":1,"finalizationDateStart":"2024-01-01","finalizationDateEnd":"2024-01-02"}'


def test_call_api(acquisition_fetcher):
    """Test call_api method with a mocked API response."""
    url = "http://test-api.com/test"
    response_data = {"message": "Success"}

    with requests_mock.Mocker() as mocker:
        mocker.post(url, json=response_data, status_code=200)

        response, message = acquisition_fetcher.call_api(url, "POST", body={"key": "value"})

        assert message == "Success"
        assert response.json() == response_data

def test_fetch_data_from_view(acquisition_fetcher):
    """Test fetch_data_from_view with a mocked API response."""
    acquisition_id = 123
    url = AcquisitionFetcher.API_DICT["view"]["url"].format(acquisition_id=acquisition_id)
    response_data = {"data": "test"}

    with requests_mock.Mocker() as mocker:
        mocker.get(url, json=response_data, status_code=200)

        result = acquisition_fetcher.fetch_data_from_view(acquisition_id)

        assert result == response_data


