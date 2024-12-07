import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from requests import HTTPError

from scrape.acquisition_fetcher import AcquisitionFetcher


@pytest.fixture
def fetcher():
    """Create an instance of AcquisitionFetcher without any db connection."""
    return AcquisitionFetcher()


def test_call_api_get_success(fetcher):
    """Test a successful GET request in call_api."""
    url = "http://example.com/api/resource"
    with patch("scrape.request_strategy.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"message": "Success"}

        response, message = fetcher.call_api(url, "GET")

        assert message == "Success"
        assert response.status_code == 200
        assert response.json() == {"message": "Success"}
        mock_get.assert_called_once_with(url, headers=fetcher.headers)


def test_call_api_post_success(fetcher):
    """Test a successful POST request in call_api."""
    url = "http://example.com/api/resource"
    body = {"key": "value"}
    with patch("scrape.request_strategy.requests.post") as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {"message": "Created"}

        response, message = fetcher.call_api(url, "POST", body=body)

        assert message == "Success"
        assert response.status_code == 201
        assert response.json() == {"message": "Created"}
        mock_post.assert_called_once_with(url, headers=fetcher.headers, data=body)


def test_fetch_data_for_one_day(fetcher):
    """Test fetching data for a single day with mock data."""
    finalization_day = datetime(2024, 1, 1)
    mock_response_data = {"items": [{"id": 1, "name": "Item1"}, {"id": 2, "name": "Item2"}]}
    empty_response_data = {"items": []}

    with patch.object(fetcher, "call_api") as mock_call_api:
        mock_call_api.side_effect = [
            (MagicMock(status_code=200, json=lambda: mock_response_data), "Success"),
            (MagicMock(status_code=200, json=lambda: empty_response_data), "Success")
        ]

        result = fetcher.fetch_data_for_one_day(finalization_day=finalization_day)

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        assert mock_call_api.call_count == 2


def test_fetch_data_from_acquisitions(fetcher):
    """Test fetching data over a date range with mocked daily data."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 3)
    mock_daily_data = [{"id": 1, "name": "Item1"}, {"id": 2, "name": "Item2"}]

    with patch.object(fetcher, "fetch_data_for_one_day", return_value=mock_daily_data) as mock_fetch_one_day:
        result = fetcher.fetch_data_from_acquisitions(start_date, end_date)

        assert len(result) == 6
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        mock_fetch_one_day.assert_called()


def test_fetch_data_from_view_success(fetcher):
    """Test fetch_data_from_view with a successful API call."""
    acquisition_id = 12345
    mock_response_data = {"details": "Acquisition details"}

    with patch.object(fetcher, "call_api", return_value=(
            MagicMock(status_code=200, json=lambda: mock_response_data), "Success")) as mock_call_api:
        result = fetcher.fetch_data_from_view(acquisition_id)

        assert result == mock_response_data
        mock_call_api.assert_called_once_with(
            fetcher.API_DICT["view"]["url"].format(acquisition_id=acquisition_id),
            fetcher.API_DICT["view"]["method"]
        )


def test_fetch_data_from_view_failure(fetcher, capsys):
    """Test fetch_data_from_view with a failed API call."""
    acquisition_id = 12345
    error_message = "Error: Connection error"

    with patch.object(fetcher, "call_api", return_value=(None, error_message)) as mock_call_api:
        result = fetcher.fetch_data_from_view(acquisition_id)

        assert result is None

        captured = capsys.readouterr()
        assert error_message in captured.out

        mock_call_api.assert_called_once_with(
            fetcher.API_DICT["view"]["url"].format(acquisition_id=acquisition_id),
            fetcher.API_DICT["view"]["method"]
        )


def test_get_all_acquisitions_data(fetcher):
    """Test fetching and processing acquisition data across dates."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 2)
    mock_acquisition_data = [{"directAcquisitionId": 1}, {"directAcquisitionId": 2}]
    mock_view_data = {"details": "View data for acquisition"}

    with patch.object(fetcher, "fetch_data_from_acquisitions", return_value=mock_acquisition_data) as mock_fetch_acq, \
            patch.object(fetcher, "fetch_data_from_view", return_value=mock_view_data) as mock_fetch_view:
        result = fetcher.get_all_acquisitions_data(start_date, end_date)

        assert len(result) == 2
        assert result[0] == mock_view_data
        assert result[1] == mock_view_data
        mock_fetch_acq.assert_called_once_with(
            finalization_date_start=start_date,
            finalization_date_end=end_date,
            acquisition_state_id=7,
            cpv_code_id=None
        )
        mock_fetch_view.assert_called()
