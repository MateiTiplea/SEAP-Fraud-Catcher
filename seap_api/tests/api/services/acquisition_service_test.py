import pytest
from unittest.mock import patch, MagicMock
from api.services.acquisition_service import AcquisitionService


@pytest.fixture
def mock_acquisition_repository():
    """Fixture for mocking AcquisitionRepository."""
    with patch("api.services.acquisition_service.AcquisitionRepository") as mock_repo:
        yield mock_repo


@pytest.fixture
def mock_item_repository():
    """Fixture for mocking ItemRepository."""
    with patch("api.services.acquisition_service.ItemRepository") as mock_repo:
        yield mock_repo


@pytest.fixture
def mock_filter_utils():
    """Fixture for mocking filter utilities."""
    with patch("api.services.acquisition_service.filter_acquisition_data") as mock_acquisition_filter, \
         patch("api.services.acquisition_service.filter_item_data") as mock_item_filter:
        yield mock_acquisition_filter, mock_item_filter


# --- TEST CASES --- #

def test_create_acquisition_with_items(
    mock_acquisition_repository, mock_item_repository, mock_filter_utils
):
    mock_acquisition_filter, mock_item_filter = mock_filter_utils

    # Setup mock return values
    mock_acquisition_filter.return_value = {"acquisition_id": "A123"}
    mock_item_filter.return_value = {"name": "Test Item"}

    acquisition_data = {
        "directAcquisitionID": "A123",
        "directAcquisitionName": "Test Acquisition",
    }
    items_data = [
        {"catalogItemName": "Item 1"},
        {"catalogItemName": "Item 2"},
    ]

    result = AcquisitionService.create_acquisition_with_items(
        acquisition_data, items_data
    )

    # Assertions
    mock_acquisition_repository.insert_acquisition.assert_called_once_with(
        {"acquisition_id": "A123"}
    )
    assert mock_item_repository.insert_item.call_count == 2
    assert result == mock_acquisition_repository.insert_acquisition.return_value


def test_get_acquisition_with_items(mock_acquisition_repository):
    # Mock return value
    mock_acquisition_repository.get_acquisition_with_items.return_value = {
        "acquisition_id": "A123",
        "items": [{"name": "Test Item"}],
    }

    result = AcquisitionService.get_acquisition_with_items(1)

    mock_acquisition_repository.get_acquisition_with_items.assert_called_once_with(1)
    assert result["acquisition_id"] == "A123"
    assert result["items"] == [{"name": "Test Item"}]


def test_update_acquisition(mock_acquisition_repository, mock_filter_utils):
    mock_acquisition_filter, _ = mock_filter_utils

    # Mock return value
    mock_acquisition_filter.return_value = {"name": "Updated Acquisition"}

    result = AcquisitionService.update_acquisition("A123", {"directAcquisitionName": "Updated Acquisition"})

    mock_acquisition_repository.update_acquisition.assert_called_once_with(
        "A123", {"name": "Updated Acquisition"}
    )
    assert result == mock_acquisition_repository.update_acquisition.return_value


def test_delete_acquisition(mock_acquisition_repository, mock_item_repository):
    # Setup mock return values
    mock_item_repository.get_items_by_acquisition.return_value = [
        MagicMock(id=1), MagicMock(id=2)
    ]
    mock_acquisition_repository.delete_acquisition.return_value = True

    result = AcquisitionService.delete_acquisition("A123")

    # Assertions
    mock_item_repository.delete_item.assert_any_call(1)
    mock_item_repository.delete_item.assert_any_call(2)
    mock_acquisition_repository.delete_acquisition.assert_called_once_with("A123")
    assert result is True


def test_get_all_acquisitions(mock_acquisition_repository):
    # Mock return value
    mock_acquisition_repository.get_all_acquisitions.return_value = [
        {"acquisition_id": "A123"},
        {"acquisition_id": "A124"},
    ]

    result = AcquisitionService.get_all_acquisitions()

    mock_acquisition_repository.get_all_acquisitions.assert_called_once()
    assert len(result) == 2
    assert result[0]["acquisition_id"] == "A123"


def test_get_acquisitions_by_cpv_code_id(mock_acquisition_repository):
    # Mock return value
    mock_acquisition_repository.get_acquisitions_by_cpv_code_id.return_value = [
        {"acquisition_id": "A125"},
        {"acquisition_id": "A126"},
    ]

    result = AcquisitionService.get_acquisitions_by_cpv_code_id(101)

    mock_acquisition_repository.get_acquisitions_by_cpv_code_id.assert_called_once_with(101)
    assert len(result) == 2
    assert result[0]["acquisition_id"] == "A125"
